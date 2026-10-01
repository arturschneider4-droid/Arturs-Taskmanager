from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import QDateEdit, QDialog, QHeaderView, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from .repositories import QuerySpec
from .task_model import ControlMode, TaskDraft
from .task_store import CommandResult, SaveTask, TaskStore


@dataclass(frozen=True)
class FollowUpItem:
    task_id: int
    title: str
    person: str
    mode: ControlMode
    waiting_days: int
    follow_up_date: date | None
    overdue: bool


class FollowUpService:
    def __init__(self, store: TaskStore, clock=datetime.now):
        self.store = store
        self.repository = store.repository
        self.clock = clock

    def _assign(self, task_id: int, person: str, follow_up_date: date | None, mode: ControlMode) -> CommandResult:
        person = person.strip()
        if not person:
            return CommandResult(False, task_id, "Person oder Organisation ist erforderlich")
        if follow_up_date is None:
            return CommandResult(False, task_id, "Wiedervorlage ist erforderlich")
        record = self.repository.get(task_id)
        if record is None:
            return CommandResult(False, task_id, "Aufgabe nicht gefunden")
        draft = replace(
            record.draft, control_mode=mode, responsible_party=person,
            delegated_at=self.clock(), follow_up_date=follow_up_date,
        )
        return self.store.apply(SaveTask(draft, task_id))

    def delegate(self, task_id: int, person: str, follow_up_date: date | None) -> CommandResult:
        return self._assign(task_id, person, follow_up_date, ControlMode.DELEGATED)

    def wait(self, task_id: int, person: str, follow_up_date: date | None) -> CommandResult:
        return self._assign(task_id, person, follow_up_date, ControlMode.WAITING)

    def follow_up(self, task_id: int, next_follow_up: date | None) -> CommandResult:
        if next_follow_up is None:
            return CommandResult(False, task_id, "Neue Wiedervorlage ist erforderlich")
        record = self.repository.get(task_id)
        if record is None:
            return CommandResult(False, task_id, "Aufgabe nicht gefunden")
        return self.store.apply(SaveTask(replace(record.draft, last_contact_at=self.clock(), follow_up_date=next_follow_up), task_id))

    def reclaim(self, task_id: int) -> CommandResult:
        record = self.repository.get(task_id)
        if record is None:
            return CommandResult(False, task_id, "Aufgabe nicht gefunden")
        draft = replace(
            record.draft, control_mode=ControlMode.SELF, responsible_party=None,
            delegated_at=None, expected_response_at=None, follow_up_date=None,
        )
        return self.store.apply(SaveTask(draft, task_id))

    def item(self, task_id: int, today: date | None = None) -> FollowUpItem:
        today = today or self.clock().date()
        record = self.repository.get(task_id)
        if record is None:
            raise ValueError("Aufgabe nicht gefunden")
        started = record.draft.delegated_at.date() if record.draft.delegated_at else record.created_at.date()
        follow_up = record.draft.follow_up_date
        return FollowUpItem(
            task_id, record.draft.title, record.draft.responsible_party or "",
            record.draft.control_mode, max(0, (today - started).days), follow_up,
            bool(follow_up and follow_up < today and record.draft.status != "Erledigt"),
        )

    def items(self, mode: ControlMode | None = None, today: date | None = None) -> list[FollowUpItem]:
        specs = [QuerySpec(control_mode=mode)] if mode else [QuerySpec(control_mode=ControlMode.DELEGATED), QuerySpec(control_mode=ControlMode.WAITING)]
        return [self.item(summary.id, today) for spec in specs for summary in self.repository.query(spec) if summary.status != "Erledigt"]


class AssignmentDialog(QDialog):
    assigned = Signal(int)
    def __init__(self, service: FollowUpService, task_id: int, mode: ControlMode, parent=None):
        super().__init__(parent); self.service = service; self.task_id = task_id; self.mode = mode
        self.setWindowTitle("Delegieren" if mode is ControlMode.DELEGATED else "Warten auf")
        root = QVBoxLayout(self); self.person_edit = QLineEdit(); self.person_edit.setPlaceholderText("Person oder Organisation")
        self.follow_up_edit = QDateEdit(); self.follow_up_edit.setCalendarPopup(True); self.follow_up_edit.setDate(QDate.currentDate().addDays(2))
        self.feedback = QLabel(); self.save_button = QPushButton("Übernehmen")
        for widget in (self.person_edit, self.follow_up_edit, self.feedback, self.save_button): root.addWidget(widget)
        self.save_button.clicked.connect(self._save)
    def _save(self):
        target = self.follow_up_edit.date().toPython()
        operation = self.service.delegate if self.mode is ControlMode.DELEGATED else self.service.wait
        result = operation(self.task_id, self.person_edit.text(), target)
        if not result.ok: self.feedback.setText(result.message); return
        self.assigned.emit(self.task_id); self.accept()


class FollowUpView(QWidget):
    next_follow_up_requested = Signal(int)
    task_selected = Signal(int)
    columns = ("Aufgabe", "Person", "Wartezeit", "Wiedervorlage")

    def __init__(self, service: FollowUpService, mode: ControlMode | None, today: date | None = None, parent=None):
        super().__init__(parent)
        self.service = service
        self.today = today or date.today()
        self.mode = mode
        self.metric_filter = None
        root = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(self.columns)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for column in (1,2,3): self.tree.header().setSectionResizeMode(column,QHeaderView.ResizeToContents)
        self.tree.itemClicked.connect(lambda item, _column: self.task_selected.emit(item.data(0, 256)) if item.data(0, 256) else None)
        root.addWidget(self.tree)
        self.service.store.changed.connect(lambda change: self.refresh() if "tasks" in change.domains else None)
        self.refresh()

    def column_names(self):
        return self.columns

    def people(self):
        return [self.tree.topLevelItem(index).text(0) for index in range(self.tree.topLevelItemCount())]

    def refresh(self):
        self.tree.clear()
        groups = {}
        mode = None if self.metric_filter == "follow_ups" else self.mode
        items = self.service.items(mode, self.today)
        if self.metric_filter == "follow_ups":
            items = [self.service.item(summary.id,self.today) for summary in self.service.repository.query(QuerySpec(metric_filter="follow_ups",today=self.today))]
        for item in items:
            if self.metric_filter == "follow_ups" and (item.follow_up_date is None or item.follow_up_date > self.today): continue
            groups.setdefault(item.person, []).append(item)
        for person, items in sorted(groups.items()):
            group = QTreeWidgetItem([person or "Selbst nachfassen"])
            self.tree.addTopLevelItem(group)
            group.setFirstColumnSpanned(True)
            for item in items:
                due = item.follow_up_date.strftime("%d.%m.%Y") if item.follow_up_date else "—"
                child = QTreeWidgetItem([item.title, item.person, f"{item.waiting_days} Tage", due])
                child.setData(0, 256, item.task_id)
                child.setToolTip(0, item.title)
                group.addChild(child)
            group.setExpanded(True)

    def follow_up_now(self, task_id: int):
        record = self.service.repository.get(task_id)
        next_date = record.draft.follow_up_date if record else None
        if next_date is not None:
            self.service.follow_up(task_id, next_date)
            self.refresh()
        self.next_follow_up_requested.emit(task_id)


class WaitingView(FollowUpView):
    def __init__(self, service, today=None, parent=None):
        super().__init__(service, ControlMode.WAITING, today, parent)


class DelegatedView(FollowUpView):
    def __init__(self, service, today=None, parent=None):
        super().__init__(service, ControlMode.DELEGATED, today, parent)


class PeopleAgendaView(FollowUpView):
    def __init__(self, service, today=None, parent=None):
        super().__init__(service, None, today, parent)

    def add_talking_point(self, person: str, title: str) -> int:
        task_id = self.service.repository.save(TaskDraft(
            title=title, control_mode=ControlMode.WAITING, responsible_party=person,
            follow_up_date=self.today, people_tags=(person,),
        ))
        self.refresh()
        return task_id
