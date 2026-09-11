"""V8 premium Eisenhower presentation layer.

The existing Eisenhower widgets and priority/task business logic remain the
source_of_truth. This module only presents the four existing priority lanes as
quiet enterprise quadrants. Its responsive presentation relies on the
existing Qt grid layout.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QLabel


QUADRANTS = (
    ("important_urgent", "Wichtig & dringend", "Sofort handeln"),
    ("important_not_urgent", "Wichtig & nicht dringend", "Planen"),
    ("not_important_urgent", "Nicht wichtig & dringend", "Delegieren"),
    ("not_important_not_urgent", "Nicht wichtig & nicht dringend", "Reduzieren"),
)


class V8Eisenhower:
    """Premium presentation controller for the existing Eisenhower lanes."""

    def __init__(self, window):
        self.window = window
        self.lanes = getattr(window, "ecols", {})
        self._install()

    def _install(self):
        self.apply()
        QTimer.singleShot(0, self.apply)

    def apply(self):
        """Reapply presentation to the functional priority lane widgets."""
        self.lanes = getattr(self.window, "ecols", self.lanes)
        for priority, title, action in QUADRANTS:
            lane = self.lanes.get(priority)
            if lane is not None:
                self._style_lane(lane, title, action)

    @staticmethod
    def _style_lane(lane, title, action):
        parent = lane.parentWidget()
        if parent is not None:
            parent.setObjectName("v8EisenhowerQuadrant")
            parent.setMinimumWidth(0)
            parent.setStyleSheet(
                "QFrame#v8EisenhowerQuadrant{background:#FFFFFF;"
                "border:1px solid #DCE4E9;border-radius:8px;}"
            )
            for child in parent.findChildren(QLabel):
                child.setObjectName("v8EisenhowerTitle")
                child.setStyleSheet(
                    "QLabel#v8EisenhowerTitle{color:#172B3A;padding:8px 4px 4px;"
                    "font-size:10pt;font-weight:700;}"
                )
                child.setToolTip(action)

        lane.setObjectName("v8EisenhowerLane")
        lane.setSpacing(7)
        lane.setContentsMargins(7, 5, 7, 7)
        lane.setSelectionMode(lane.SelectionMode.SingleSelection)
        lane.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        lane.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lane.setStyleSheet(
            "QListWidget#v8EisenhowerLane{background:transparent;border:0;"
            "outline:none;padding:4px;}"
            "QListWidget#v8EisenhowerLane::item{background:#FFFFFF;"
            "border:1px solid #E1E8EC;border-radius:7px;padding:10px 11px;"
            "margin:1px 0;color:#263844;}"
            "QListWidget#v8EisenhowerLane::item:hover{background:#F8FAFB;"
            "border-color:#C8D6DE;}"
            "QListWidget#v8EisenhowerLane::item:selected{background:#EAF3F9;"
            "border-color:#8FB9D0;color:#172B3A;}"
        )
        for row in range(lane.count()):
            item = lane.item(row)
            item.setData(Qt.UserRole + 1, "v8EisenhowerCard")
            font = QFont(item.font())
            font.setBold(True)
            item.setFont(font)
            item.setForeground(QColor("#263844"))
            item.setToolTip(item.text().replace("\n", " · "))
        lane.style().unpolish(lane)
        lane.style().polish(lane)
        lane.update()


def install_v8_eisenhower(window):
    """Install presentation only; existing priority lists remain the source_of_truth."""
    existing = getattr(window, "_v8_eisenhower", None)
    if existing is not None:
        existing.apply()
        return existing
    controller = V8Eisenhower(window)
    window._v8_eisenhower = controller
    return controller
