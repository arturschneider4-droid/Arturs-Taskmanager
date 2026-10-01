from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

from PySide6.QtCore import Qt, Signal, QDate, QLocale
from PySide6.QtWidgets import QCalendarWidget, QPushButton, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from .task_store import SaveTask, TaskStore


@dataclass(frozen=True)
class CalendarItem:
    task_id: int
    title: str
    planning_date: date | None
    deadline: date | None
    planning_marker: str = "●"
    deadline_marker: str = "◆"


class CalendarView(QWidget):
    task_selected = Signal(int)
    deadline_action_label = "Deadline ausdrücklich verschieben"

    def __init__(self, store: TaskStore, today: date | None = None, parent=None):
        super().__init__(parent)
        self.store = store; self.today = today or date.today(); self._items = []
        root = QVBoxLayout(self)
        self.legend_label = QLabel("● Planung   ◆ Deadline")
        self.listing = QListWidget()
        self.listing.itemClicked.connect(lambda item: self.task_selected.emit(item.data(Qt.UserRole)))
        self.listing.itemActivated.connect(lambda item: self.task_selected.emit(item.data(Qt.UserRole)))
        self.calendar = QCalendarWidget(); self.calendar.setSelectedDate(QDate(self.today))
        self.calendar.setGridVisible(True)
        self.calendar.setLocale(QLocale(QLocale.German, QLocale.Germany))
        self.calendar.setFirstDayOfWeek(Qt.Monday)
        self.calendar.setMaximumHeight(270)
        root.addWidget(self.calendar)
        root.addWidget(self.legend_label); root.addWidget(self.listing)
        self.plan_button = QPushButton("Planung auf gewählten Tag")
        self.deadline_button = QPushButton(self.deadline_action_label)
        self.feedback = QLabel(); self.feedback.setWordWrap(True)
        buttons = QHBoxLayout(); buttons.addWidget(self.plan_button); buttons.addWidget(self.deadline_button)
        root.addLayout(buttons); root.addWidget(self.feedback)
        self.plan_button.clicked.connect(lambda: self._apply_selected_date(False))
        self.deadline_button.clicked.connect(lambda: self._apply_selected_date(True))
        self.store.changed.connect(lambda change: self.refresh() if "tasks" in change.domains else None)
        self.refresh()

    def refresh(self):
        self._items = [CalendarItem(item.id, item.title, item.planning_date, item.deadline) for item in self.store.repository.query()]
        self.listing.clear()
        for item in self._items:
            planning = item.planning_date.strftime("%d.%m.") if item.planning_date else "—"
            deadline = item.deadline.strftime("%d.%m.") if item.deadline else "—"
            row = QListWidgetItem(f"● {planning}  ◆ {deadline}  {item.title}")
            row.setData(Qt.UserRole, item.task_id); self.listing.addItem(row)

    def _apply_selected_date(self, deadline):
        selected = self.listing.currentItem()
        if selected is None:
            self.feedback.setText("Bitte zuerst eine Aufgabe auswählen"); return
        task_id = selected.data(Qt.UserRole)
        operation = self.move_deadline_explicitly if deadline else self.move_planning_date
        if operation(task_id, self.calendar.selectedDate().toPython()):
            self.feedback.setText("Deadline verschoben" if deadline else "Planung verschoben; Deadline bleibt unverändert")

    def item_for(self, task_id):
        return next(item for item in self._items if item.task_id == task_id)

    def _move(self, task_id, field, value):
        record = self.store.repository.get(task_id)
        if record is None or not isinstance(value, date): return False
        return self.store.apply(SaveTask(replace(record.draft, **{field: value}), task_id)).ok

    def move_planning_date(self, task_id: int, target: date) -> bool:
        return self._move(task_id, "planning_date", target)

    def move_deadline_explicitly(self, task_id: int, target: date) -> bool:
        return self._move(task_id, "deadline", target)
