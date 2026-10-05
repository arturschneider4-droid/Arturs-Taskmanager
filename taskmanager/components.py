from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .design_tokens import IconRegistry


class StatefulWidget:
    def set_state(self, state: str) -> None:
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)


class PrimaryButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("variant", "primary")
        self.setAccessibleName(text)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


class IconButton(QPushButton):
    def __init__(self, icon_name: str, accessible_name: str, parent=None):
        super().__init__(parent)
        self.setIcon(IconRegistry().icon(icon_name))
        self.setAccessibleName(accessible_name)
        self.setToolTip(accessible_name)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


class Chip(QLabel, StatefulWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("role", "chip")


class Toast(QFrame, StatefulWidget):
    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        self.message_label = QLabel(message)
        layout.addWidget(self.message_label)
        self.setAccessibleName(message)


class MetricCard(QPushButton):
    activated = Signal(str)

    def __init__(self, label: str, value: int, filter_key: str, parent=None):
        super().__init__(parent)
        self.setProperty("role", "metric-card")
        self.filter_key = filter_key
        layout = QVBoxLayout(self)
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("metricValue")
        self.label = QLabel(label)
        self.label.setObjectName("metricCaption")
        self.label.setWordWrap(True)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.addWidget(self.label)
        layout.addWidget(self.value_label)
        self.setAccessibleName(f"{label}: {value}")
        self.clicked.connect(lambda: self.activated.emit(self.filter_key))


class TaskRow(QFrame):
    selected = Signal(int)
    completed = Signal(int)

    def __init__(self, task_id: int, title: str, project: str, schedule: str, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.setProperty("role", "task-row")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        self.complete_button = IconButton("check", f"{title} erledigen")
        self.title_button = QPushButton(title)
        self.title_button.setAccessibleName(f"Aufgabe öffnen: {title}")
        self.project_label = QLabel(project)
        self.schedule_label = QLabel(schedule)
        layout.addWidget(self.complete_button)
        layout.addWidget(self.title_button, 1)
        layout.addWidget(self.project_label)
        layout.addWidget(self.schedule_label)
        self.title_button.clicked.connect(lambda: self.selected.emit(self.task_id))
        self.complete_button.clicked.connect(lambda: self.completed.emit(self.task_id))


class EmptyState(QWidget, StatefulWidget):
    def __init__(self, title: str, action_text: str, icon_name: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel()
        icon.setPixmap(IconRegistry().icon(icon_name).pixmap(32, 32))
        self.title_label = QLabel(title)
        self.action_button = PrimaryButton(action_text)
        layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignCenter)
