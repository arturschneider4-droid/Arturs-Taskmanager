"""V8 premium Kanban presentation layer.

The existing Kanban widgets and task business logic remain the source of truth.
This module only styles the already-created status lanes. Its responsive
presentation is intentionally based on the existing Qt layout.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont


STATUS_LANES = (
    ("Offen", "#1689C5"),
    ("In Arbeit", "#D28A22"),
    ("Erledigt", "#4D8B63"),
)


class V8Kanban:
    """Premium presentation controller for the existing Kanban lanes."""

    def __init__(self, window):
        self.window = window
        self.lanes = getattr(window, "kcols", {})
        self._install()

    def _install(self):
        self.apply()
        QTimer.singleShot(0, self.apply)

    def apply(self):
        """Reapply presentation to the functional lane widgets."""
        self.lanes = getattr(self.window, "kcols", self.lanes)
        for status, accent in STATUS_LANES:
            lane = self.lanes.get(status)
            if lane is None:
                continue
            self._style_lane(lane, accent)

    @staticmethod
    def _style_lane(lane, accent):
        lane.setObjectName("v8KanbanLane")
        lane.setSpacing(8)
        lane.setContentsMargins(6, 6, 6, 6)
        lane.setSelectionMode(lane.SelectionMode.SingleSelection)
        lane.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        lane.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lane.setStyleSheet(
            "QListWidget#v8KanbanLane{background:#FFFFFF;border:1px solid #DCE4E9;"
            "border-radius:7px;padding:6px;}"
            "QListWidget#v8KanbanLane::item{background:#F8FAFB;border:1px solid #E3E9ED;"
            "border-radius:6px;padding:9px 10px;margin:2px 0;color:#263844;}"
            "QListWidget#v8KanbanLane::item:hover{background:#F1F5F7;border-color:#C8D6DE;}"
            "QListWidget#v8KanbanLane::item:selected{background:#E7F1FA;border-color:#B8D2E3;color:#172B3A;}"
        )
        for row in range(lane.count()):
            item = lane.item(row)
            item.setData(Qt.UserRole + 1, "v8KanbanCard")
            font = QFont(item.font())
            font.setBold(True)
            item.setFont(font)
            item.setForeground(QColor("#263844"))
            item.setToolTip(item.text().replace("\n", " · "))
        lane.setProperty("v8LaneAccent", accent)
        lane.style().unpolish(lane)
        lane.style().polish(lane)
        lane.update()


def install_v8_kanban(window):
    """Install the presentation layer without replacing task source_of_truth."""
    existing = getattr(window, "_v8_kanban", None)
    if existing is not None:
        existing.apply()
        return existing
    controller = V8Kanban(window)
    window._v8_kanban = controller
    return controller
