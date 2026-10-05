from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QPainter, QColor
from PySide6.QtWidgets import QLabel, QButtonGroup, QPushButton, QVBoxLayout, QWidget

from .design_tokens import IconRegistry


class Route(str, Enum):
    DASHBOARD = "dashboard"
    MY_DAY = "my_day"
    INBOX = "inbox"
    NEXT_SEVEN = "next_seven"
    WAITING = "waiting"
    DELEGATED = "delegated"
    ALL_TASKS = "all_tasks"
    TASKS = "tasks"
    KANBAN = "kanban"
    EISENHOWER = "eisenhower"
    CALENDAR = "calendar"
    WEEKLY_REVIEW = "weekly_review"
    SETTINGS = "settings"
    HELP = "help"


ROUTE_LABELS = {
    Route.DASHBOARD: ("dashboard", "Executive Dashboard"),
    Route.MY_DAY: ("today", "Mein Tag"),
    Route.INBOX: ("inbox", "Eingang"),
    Route.NEXT_SEVEN: ("calendar", "Nächste 7 Tage"),
    Route.WAITING: ("waiting", "Warten auf"),
    Route.DELEGATED: ("delegated", "Delegiert"),
    Route.ALL_TASKS: ("tasks", "Alle Aufgaben"),
    Route.TASKS: ("tasks", "Aufgabenliste"),
    Route.KANBAN: ("kanban", "Kanban"),
    Route.EISENHOWER: ("eisenhower", "Eisenhower"),
    Route.CALENDAR: ("calendar", "Kalender"),
    Route.WEEKLY_REVIEW: ("review", "Wochenreview"),
    Route.SETTINGS: ("settings", "Einstellungen"),
    Route.HELP: ("help", "Hilfe"),
}


class Navigation(QWidget):
    route_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("v10Navigation")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._buttons = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)
        self.brand = QLabel("ARTUR / WORK")
        self.brand.setObjectName("navBrand")
        layout.addWidget(self.brand)
        icons = IconRegistry()
        for route in Route:
            icon_name, label = ROUTE_LABELS[route]
            pixmap = icons.icon(icon_name).pixmap(24, 24)
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor("#E2EAF0"))
            painter.end()
            button = QPushButton(QIcon(pixmap), label)
            button.setObjectName(f"nav_{route.value}")
            button.setAccessibleName(label)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, value=route: self.route_requested.emit(value))
            self._group.addButton(button)
            self._buttons[route] = button
            layout.addWidget(button)
        layout.addStretch(1)

    def button_for(self, route: Route) -> QPushButton:
        return self._buttons[route]

    def set_active(self, route: Route) -> None:
        for item, button in self._buttons.items():
            active = item is route
            button.setChecked(active)
            button.setProperty("active", active)
            button.style().unpolish(button)
            button.style().polish(button)

    def set_compact(self, compact: bool) -> None:
        self.brand.setVisible(not compact)
        for route, button in self._buttons.items():
            button.setText("" if compact else ROUTE_LABELS[route][1])
            button.setToolTip(ROUTE_LABELS[route][1] if compact else "")
