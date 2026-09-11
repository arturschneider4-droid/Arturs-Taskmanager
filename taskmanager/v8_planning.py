"""V8 premium Planning presentation layer; existing planning data remains source_of_truth.

The module only styles and lays out the existing QListWidget lanes. It deliberately
contains no task-loading implementation. The three existing planning groups are
preserved and the layout is responsive to the available workspace width.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QFrame, QLabel


PLANNING_LANES = (
    ("Heute", "HEUTE"),
    ("Diese Woche", "DIESE WOCHE"),
    ("Später", "SPÄTER"),
)


class V8Planning:
    """Presentation-only controller for the existing planning lanes."""

    def __init__(self, window):
        self.window = window
        self.lanes = getattr(window, "pcols", {})
        self._installed = False

    def apply(self):
        self.lanes = getattr(self.window, "pcols", {})
        if not self.lanes:
            return
        for key, heading in PLANNING_LANES:
            widget = self.lanes.get(key)
            if widget is None:
                continue
            parent = widget.parentWidget()
            if parent is not None:
                parent.setObjectName("v8PlanningLane")
                parent.setStyleSheet(
                    "QFrame#v8PlanningLane{background:#FFFFFF;border:1px solid #DCE4E9;"
                    "border-radius:8px;}"
                )
                for label in parent.findChildren(QLabel):
                    label.setObjectName("v8PlanningLaneTitle")
                    label.setStyleSheet(
                        "QLabel#v8PlanningLaneTitle{color:#172B3A;padding:8px 4px 4px;"
                        "font-size:10pt;font-weight:700;}"
                    )
                    if not label.text().strip():
                        label.setText(heading)
            widget.setObjectName("v8PlanningLaneList")
            widget.setSpacing(7)
            widget.setUniformItemSizes(False)
            widget.setFrameShape(QFrame.NoFrame)
            widget.setStyleSheet(
                "QListWidget#v8PlanningLaneList{background:transparent;border:0;outline:none;"
                "padding:4px;}"
                "QListWidget#v8PlanningLaneList::item{background:#FFFFFF;border:1px solid #E1E8EC;"
                "border-radius:7px;padding:10px 11px;margin:1px 0;color:#263844;}"
                "QListWidget#v8PlanningLaneList::item:hover{background:#F8FAFB;"
                "border-color:#C8D6DE;}"
                "QListWidget#v8PlanningLaneList::item:selected{background:#EAF3F9;"
                "border-color:#8FB9D0;color:#172B3A;}"
            )
            widget.setMinimumWidth(0)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            for row in range(widget.count()):
                item = widget.item(row)
                font = QFont(item.font())
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QColor("#263844"))
                item.setToolTip(item.text().replace("\n", " · "))
        self._installed = True

    def install(self):
        self.apply()
        QTimer.singleShot(0, self.apply)
        return self


def install_v8_planning(window):
    """Install the V8 planning presentation without changing task behavior."""
    controller = getattr(window, "_v8_planning", None)
    if controller is None:
        controller = V8Planning(window)
        window._v8_planning = controller
    return controller.install()
