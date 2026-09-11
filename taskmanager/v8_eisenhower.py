"""V8 premium Eisenhower presentation layer.

The existing Eisenhower widgets and priority/task business logic remain the
source_of_truth. This module only presents the four existing priority lanes as
quiet enterprise quadrants. Its responsive presentation relies on the
existing Qt grid layout.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont


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
            if lane is None:
                continue
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
            labels = parent.findChildren(type(lane.parentWidget().layout().itemAt(0).widget())) if parent.layout() else []
            for child in parent.findChildren(__import__("PySide6.QtWidgets", fromlist=["QLabel"]).QLabel):
                child.setObjectName("v8EisenhowerTitle")
                child.setText(title)
                font = QFont(child.font())
                font.setBold(True)
                child.setFont(font)
                child.setToolTip(action)
                child.setStyleSheet(
                    "QLabel#v8EisenhowerTitle{color:#172B3A;padding:8px 4px 4px;"
                    "font-size:10pt;font-weight:700;}"
                )

        lane.setObjectName("v8EisenhowerLane")
        lane.setSpacing(7)
        lane.setContentsMargins(6, 5, 6, 6)
        lane.setSelectionMode(lane.SelectionMode.SingleSelection)
        lane.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        lane.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lane.setStyleSheet(
            "QListWidget#v8EisenhowerLane{background:#FFFFFF;border:0;"
            "outline:none;padding:4px;}"
            "QListWidget#v8EisenhowerLane::item{background:#F8FAFB;"
            "border:1px solid #E3E9ED;border-radius:6px;padding:9px 10px;"
            "margin:2px 0;color:#263844;}"
            "QListWidget#v8EisenhowerLane::item:hover{background:#F1F5F7;"
            "border-color:#C8D6DE;}"
            "QListWidget#v8EisenhowerLane::item:selected{background:#E7F1FA;"
            "border-color:#B8D2E3;color:#172B3A;}"
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
