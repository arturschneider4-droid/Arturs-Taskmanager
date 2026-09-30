from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

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
    deadline_action_label = "Deadline ausdrücklich verschieben"

    def __init__(self, store: TaskStore, today: date | None = None, parent=None):
        super().__init__(parent)
        self.store = store; self.today = today or date.today(); self._items = []
        root = QVBoxLayout(self)
        self.legend_label = QLabel("● Planung   ◆ Deadline")
        self.listing = QListWidget()
        root.addWidget(self.legend_label); root.addWidget(self.listing)
        self.store.changed.connect(lambda change: self.refresh() if "tasks" in change.domains else None)
        self.refresh()

    def refresh(self):
        self._items = [CalendarItem(item.id, item.title, item.planning_date, item.deadline) for item in self.store.repository.query()]
        self.listing.clear()
        for item in self._items:
            planning = item.planning_date.strftime("%d.%m.") if item.planning_date else "—"
            deadline = item.deadline.strftime("%d.%m.") if item.deadline else "—"
            self.listing.addItem(f"● {planning}  ◆ {deadline}  {item.title}")

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
