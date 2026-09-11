"""V8 premium Planning presentation layer; existing planning data remains source_of_truth.

The module only styles and lays out the existing QListWidget lanes. It deliberately
contains no task-loading implementation. The three existing planning groups are
preserved and the layout is responsive to the available workspace width.
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame


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
            widget.setObjectName("v8PlanningLaneList")
            widget.setSpacing(6)
            widget.setUniformItemSizes(False)
            widget.setFrameShape(QFrame.NoFrame)
            widget.setStyleSheet(
                "QListWidget{background:transparent;border:0;outline:none;}"
                "QListWidget::item{background:#FFFFFF;border:1px solid #E1E8EC;"
                "border-radius:7px;padding:10px 12px;margin:0;}"
                "QListWidget::item:hover{border-color:#B8CDD9;background:#FBFCFD;}"
                "QListWidget::item:selected{background:#EAF3F9;border-color:#8FB9D0;color:#172B3A;}"
            )
            widget.setMinimumWidth(0)
            widget.setHorizontalScrollBarPolicy(1)
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
