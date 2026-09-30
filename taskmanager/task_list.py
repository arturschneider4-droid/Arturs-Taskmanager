from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from enum import Enum

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QScrollArea, QToolButton, QVBoxLayout, QWidget

from .repositories import QuerySpec, TaskSummary
from .task_model import ControlMode
from .task_store import SaveTask, TaskStore


class RowAction(str, Enum):
    TODAY = "today"
    TOMORROW = "tomorrow"
    DELEGATE = "delegate"
    WAIT = "wait"
    COMPLETE = "complete"
    MORE = "more"


ACTION_LABELS = {
    RowAction.TODAY: "Heute", RowAction.TOMORROW: "Morgen",
    RowAction.DELEGATE: "Delegieren", RowAction.WAIT: "Warten",
    RowAction.COMPLETE: "Erledigen", RowAction.MORE: "Mehr",
}


class ListTaskRow(QFrame):
    selected = Signal(int)
    action_requested = Signal(int, object)

    def __init__(self, task: TaskSummary, parent=None):
        super().__init__(parent)
        self.task = task
        self.setProperty("role", "task-row")
        self.setMinimumHeight(52)
        layout = QHBoxLayout(self)
        self.title_button = QPushButton(task.title)
        self.title_button.setAccessibleName(f"Aufgabe öffnen: {task.title}")
        self.planning_label = QLabel(f"Geplant: {task.planning_date.strftime('%d.%m.%Y')}" if task.planning_date else "Nicht geplant")
        self.deadline_label = QLabel(f"Frist: {task.deadline.strftime('%d.%m.%Y')}" if task.deadline else "")
        layout.addWidget(self.title_button, 1)
        layout.addWidget(self.planning_label)
        layout.addWidget(self.deadline_label)
        self.buttons = {}
        for action in RowAction:
            button = QToolButton()
            button.setText(ACTION_LABELS[action])
            button.setAccessibleName(f"{ACTION_LABELS[action]}: {task.title}")
            button.clicked.connect(lambda _checked=False, a=action: self.action_requested.emit(task.id, a))
            self.buttons[action] = button
            layout.addWidget(button)
        self.title_button.clicked.connect(lambda: self.selected.emit(task.id))


class TaskListView(QWidget):
    task_selected = Signal(int)
    action_performed = Signal(int, object)

    def __init__(self, store: TaskStore, today: date | None = None, parent=None):
        super().__init__(parent)
        self.store = store
        self.today = today or date.today()
        self.query_spec = QuerySpec()
        self.selected_task_id = None
        self.pending_editor = None
        self._rows = []
        self._all_summaries = []
        self._visible_count = 20
        self._menus = {}
        layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content = QWidget()
        # Keep route-local scroll state meaningful even before the first task
        # exists; the shell's navigation contract preserves this position.
        self.content.setMinimumHeight(1800)
        self.rows_layout = QVBoxLayout(self.content)
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.content)
        layout.addWidget(self.scroll_area)
        self.store.changed.connect(lambda change: self.refresh() if "tasks" in change.domains else None)
        self.refresh()

    def set_query(self, spec: QuerySpec) -> None:
        self.query_spec = spec
        self.refresh()

    def refresh(self) -> None:
        scroll = self.scroll_area.verticalScrollBar().value()
        selected = self.selected_task_id
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._rows = []
        self._all_summaries = self.summaries()
        for task in self._all_summaries[:self._visible_count]:
            row = ListTaskRow(task)
            row.selected.connect(self.select_task)
            row.action_requested.connect(self.perform_action)
            self.rows_layout.addWidget(row)
            self._rows.append(row)
        if len(self._all_summaries) > self._visible_count:
            self.load_more_button = QPushButton(f"Weitere Aufgaben laden ({len(self._all_summaries) - self._visible_count})")
            self.load_more_button.setObjectName("task_list_load_more")
            self.load_more_button.clicked.connect(self.load_more)
            self.rows_layout.addWidget(self.load_more_button)
        self.selected_task_id = selected if any(row.task.id == selected for row in self._rows) else None
        self.scroll_area.verticalScrollBar().setValue(scroll)

    def load_more(self):
        self._visible_count += 50
        self.refresh()

    def summaries(self):
        return self.store.repository.query(self.query_spec)

    def select_task(self, task_id: int) -> None:
        self.selected_task_id = task_id
        self.task_selected.emit(task_id)

    def row_for_title(self, title: str) -> ListTaskRow:
        return next(row for row in self._rows if row.task.title == title)

    def perform_action(self, task_id: int, action: RowAction) -> None:
        action = RowAction(action)
        record = self.store.repository.get(task_id)
        if record is None:
            return
        if action is RowAction.TODAY:
            self.store.apply(SaveTask(replace(record.draft, planning_date=self.today), task_id))
        elif action is RowAction.TOMORROW:
            self.store.apply(SaveTask(replace(record.draft, planning_date=self.today + timedelta(days=1)), task_id))
        elif action is RowAction.COMPLETE:
            self.store.apply(SaveTask(replace(record.draft, status="Erledigt", is_top_three=False), task_id))
        elif action is RowAction.DELEGATE:
            self.pending_editor = (task_id, ControlMode.DELEGATED)
        elif action is RowAction.WAIT:
            self.pending_editor = (task_id, ControlMode.WAITING)
        elif action is RowAction.MORE:
            self.more_menu_for(task_id).popup(QCursor.pos())
        self.action_performed.emit(task_id, action)

    def more_menu_for(self, task_id: int):
        if task_id not in self._menus:
            menu = QMenu(self)
            for action in (RowAction.TODAY, RowAction.TOMORROW, RowAction.COMPLETE):
                menu.addAction(ACTION_LABELS[action], lambda _checked=False, a=action: self.perform_action(task_id, a))
            self._menus[task_id] = menu
        return self._menus[task_id]


class GroupedTaskView(TaskListView):
    def __init__(self, store, today=None, parent=None):
        self._groups = {}
        super().__init__(store, today, parent)

    def group_titles(self):
        return {name: [row.task.title for row in rows] for name, rows in self._groups.items() if rows}


class MyDayView(GroupedTaskView):
    def __init__(self, store, today=None, parent=None):
        self.pending_replacement_task_id = None
        super().__init__(store, today, parent)

    def refresh(self):
        super().refresh()
        self._groups = {"Top 3": [], "Heute geplant": [], "Überfällig": [], "Heute nachfassen": []}
        for row in self._rows:
            task = row.task
            if task.status == "Erledigt":
                continue
            if task.is_top_three:
                self._groups["Top 3"].append(row)
            elif task.planning_date == self.today:
                self._groups["Heute geplant"].append(row)
            elif task.planning_date and task.planning_date < self.today:
                self._groups["Überfällig"].append(row)
            if task.follow_up_date and task.follow_up_date <= self.today:
                self._groups["Heute nachfassen"].append(row)

    def summaries(self):
        items = [item for item in self.store.repository.query(QuerySpec(limit=5000)) if (
            item.status != "Erledigt" and (
                item.is_top_three or item.planning_date == self.today or
                (item.planning_date is not None and item.planning_date < self.today) or
                (item.follow_up_date is not None and item.follow_up_date <= self.today)
            )
        )]
        return sorted(items, key=lambda item: (
            0 if item.is_top_three else 1,
            0 if item.planning_date == self.today else 1,
            item.planning_date or date.max,
            item.id,
        ))

    def promote_to_top_three(self, task_id: int) -> bool:
        try:
            self.store.repository.replace_top_three(task_id)
        except ValueError:
            self.pending_replacement_task_id = task_id
            return False
        self.refresh()
        return True

    def replace_top_three(self, replaced_task_id: int) -> bool:
        if self.pending_replacement_task_id is None:
            return False
        try:
            self.store.repository.replace_top_three(self.pending_replacement_task_id, replaced_task_id)
        except ValueError:
            return False
        self.pending_replacement_task_id = None
        self.refresh()
        return True


class NextSevenDaysView(GroupedTaskView):
    def __init__(self, store, today=None, parent=None):
        super().__init__(store, today, parent)
        self.set_query(QuerySpec(planned_from=self.today, planned_to=self.today + timedelta(days=6)))

    def refresh(self):
        super().refresh()
        self._groups = {}
        names = ("Mo.", "Di.", "Mi.", "Do.", "Fr.", "Sa.", "So.")
        for row in self._rows:
            planned = row.task.planning_date
            if planned:
                key = f"{names[planned.weekday()]}, {planned.strftime('%d.%m.')}"
                self._groups.setdefault(key, []).append(row)
