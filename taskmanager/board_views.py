from __future__ import annotations

from dataclasses import replace

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QVBoxLayout, QWidget

from .repositories import QuerySpec
from .task_store import SaveTask, TaskStore


STATUSES = ("Offen", "In Arbeit", "Erledigt")
PRIORITIES = ("important_urgent", "important_not_urgent", "not_important_urgent", "not_important_not_urgent")


class BoardView(QWidget):
    lanes: tuple[str, ...] = ()
    field = ""

    def __init__(self, store: TaskStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.query = QuerySpec()
        self._summaries = []
        root = QVBoxLayout(self)
        lane_row = QHBoxLayout()
        self.lane_widgets = {}
        for lane in self.lanes:
            column = QWidget(); layout = QVBoxLayout(column)
            layout.addWidget(QLabel(self.label_for(lane)))
            listing = QListWidget(); layout.addWidget(listing)
            self.lane_widgets[lane] = listing; lane_row.addWidget(column)
        root.addLayout(lane_row)
        self.store.changed.connect(lambda change: self.refresh() if "tasks" in change.domains else None)
        self.refresh()

    def label_for(self, lane):
        return lane

    def set_query(self, spec: QuerySpec):
        self.query = spec; self.refresh()

    def titles(self):
        return [item.title for item in self._summaries]

    def refresh(self):
        self._summaries = self.store.repository.query(self.query)
        for listing in self.lane_widgets.values(): listing.clear()
        for item in self._summaries:
            lane = getattr(item, self.field)
            if lane in self.lane_widgets: self.lane_widgets[lane].addItem(("★ " if item.is_top_three else "") + item.title)

    def move_task(self, task_id: int, lane: str) -> bool:
        if lane not in self.lanes: return False
        record = self.store.repository.get(task_id)
        if record is None: return False
        result = self.store.apply(SaveTask(replace(record.draft, **{self.field: lane}), task_id))
        return result.ok


class KanbanView(BoardView):
    lanes = STATUSES
    field = "status"


class EisenhowerView(BoardView):
    lanes = PRIORITIES
    field = "priority"
    def label_for(self, lane):
        return {
            "important_urgent": "Wichtig & dringend", "important_not_urgent": "Wichtig",
            "not_important_urgent": "Dringend", "not_important_not_urgent": "Später",
        }[lane]
