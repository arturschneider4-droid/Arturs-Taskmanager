from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import re
from typing import Sequence

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QWidget

from .repositories import QuerySpec
from .task_model import ControlMode, TaskDraft
from .task_store import SaveTask, TaskStore


WEEKDAYS = {"montag": 0, "dienstag": 1, "mittwoch": 2, "donnerstag": 3, "freitag": 4, "samstag": 5, "sonntag": 6}
PRIORITIES = {"!wichtig": "important_not_urgent", "!dringend": "not_important_urgent", "!kritisch": "important_urgent"}
MODES = {"@warten": ControlMode.WAITING, "@delegiert": ControlMode.DELEGATED}


@dataclass(frozen=True)
class CapturePreview:
    title: str
    planning_date: date | None = None
    project: str | None = None
    priority: str = "important_not_urgent"
    control_mode: ControlMode = ControlMode.SELF
    estimated_minutes: int | None = None


def parse_capture(text: str, today: date, projects: Sequence[str]) -> CapturePreview:
    remaining = text.strip()
    planning_date = None
    if re.search(r"\bnächste\s+woche\b", remaining, re.IGNORECASE):
        planning_date = today + timedelta(days=(7 - today.weekday()))
        remaining = re.sub(r"\bnächste\s+woche\b", "", remaining, flags=re.IGNORECASE)
    elif re.search(r"\bmorgen\b", remaining, re.IGNORECASE):
        planning_date = today + timedelta(days=1)
        remaining = re.sub(r"\bmorgen\b", "", remaining, flags=re.IGNORECASE)
    elif re.search(r"\bheute\b", remaining, re.IGNORECASE):
        planning_date = today
        remaining = re.sub(r"\bheute\b", "", remaining, flags=re.IGNORECASE)
    else:
        for name, weekday in WEEKDAYS.items():
            if re.search(rf"\b{name}\b", remaining, re.IGNORECASE):
                delta = (weekday - today.weekday()) % 7 or 7
                planning_date = today + timedelta(days=delta)
                remaining = re.sub(rf"\b{name}\b", "", remaining, flags=re.IGNORECASE)
                break
    duration = None
    duration_match = re.search(r"\b(?:(\d+)h(?:(\d{1,2}))?|(?:(\d+)min))\b", remaining, re.IGNORECASE)
    if duration_match:
        hours, minutes, minutes_only = duration_match.groups()
        duration = int(minutes_only) if minutes_only else int(hours) * 60 + int(minutes or 0)
        remaining = remaining[:duration_match.start()] + remaining[duration_match.end():]
    project = None
    for candidate in projects:
        match = re.search(rf"(?<!\S)#{re.escape(candidate)}\b", remaining, re.IGNORECASE)
        if match:
            project = candidate
            remaining = remaining[:match.start()] + remaining[match.end():]
            break
    priority = "important_not_urgent"
    for token, value in PRIORITIES.items():
        if re.search(rf"(?<!\S){re.escape(token)}\b", remaining, re.IGNORECASE):
            priority = value
            remaining = re.sub(rf"(?<!\S){re.escape(token)}\b", "", remaining, flags=re.IGNORECASE)
    mode = ControlMode.SELF
    for token, value in MODES.items():
        if re.search(rf"(?<!\S){re.escape(token)}\b", remaining, re.IGNORECASE):
            mode = value
            remaining = re.sub(rf"(?<!\S){re.escape(token)}\b", "", remaining, flags=re.IGNORECASE)
    title = " ".join(remaining.split())
    return CapturePreview(title, planning_date, project, priority, mode, duration)


def is_clarified(draft: TaskDraft) -> bool:
    return bool(draft.planning_date or draft.follow_up_date or draft.status == "Ohne Termin") and draft.control_mode in ControlMode


class CaptureInput(QLineEdit):
    escape_pressed = Signal()
    tab_pressed = Signal()

    def event(self, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Tab:
            self.tab_pressed.emit()
            return True
        return super().event(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.escape_pressed.emit()
            return
        super().keyPressEvent(event)


class QuickCaptureOverlay(QFrame):
    saved = Signal(int)
    advanced_requested = Signal()

    def __init__(self, store: TaskStore, today: date | None = None, projects: Sequence[str] = (), parent=None):
        super().__init__(parent)
        self.store = store
        self.today = today or date.today()
        self.projects = tuple(projects)
        self.setObjectName("quickCaptureOverlay")
        layout = QVBoxLayout(self)
        self.input = CaptureInput()
        self.input.setObjectName("quick_capture_input")
        self.input.setPlaceholderText("Aufgabe erfassen …")
        self.input.setAccessibleName("Schnellerfassung")
        self.preview_label = QLabel()
        layout.addWidget(self.input)
        layout.addWidget(self.preview_label)
        self.preview_label.setWordWrap(True)
        buttons = QHBoxLayout()
        self.save_button = QPushButton("Aufgabe anlegen"); self.save_button.setProperty("variant", "primary")
        self.advanced_button = QPushButton("Details ergänzen"); self.cancel_button = QPushButton("Abbrechen")
        self.save_button.clicked.connect(self._save); self.advanced_button.clicked.connect(self.advanced_requested)
        self.cancel_button.clicked.connect(self.hide)
        for button in (self.save_button,self.advanced_button,self.cancel_button): buttons.addWidget(button)
        layout.addLayout(buttons)
        self.input.textChanged.connect(self._refresh_preview)
        self.input.returnPressed.connect(self._save)
        self.input.escape_pressed.connect(self.hide)
        self.input.tab_pressed.connect(self.advanced_requested.emit)

    def _preview(self) -> CapturePreview:
        connection = self.store.repository._connect()
        self._project_ids = {row["name"]: row["id"] for row in connection.execute("SELECT id,name FROM projects")}
        connection.close()
        return parse_capture(self.input.text(), self.today, tuple(dict.fromkeys((*self.projects, *self._project_ids))))

    def _refresh_preview(self) -> None:
        preview = self._preview()
        values = []
        if preview.planning_date:
            values.append(preview.planning_date.strftime("%d.%m.%Y"))
        if preview.project:
            values.append(preview.project)
        if preview.estimated_minutes:
            values.append(f"{preview.estimated_minutes} Min.")
        self.preview_label.setText(" · ".join(values) if values else "Wird im Eingang gespeichert")

    def _save(self) -> None:
        preview = self._preview()
        if not preview.title:
            self.preview_label.setText("Titel erforderlich")
            return
        if preview.control_mode is not ControlMode.SELF:
            self.preview_label.setText("Person oder Organisation in den erweiterten Feldern ergänzen")
            self.advanced_requested.emit()
            return
        if preview.estimated_minutes is not None and preview.estimated_minutes <= 0:
            self.preview_label.setText("Geschätzte Dauer muss positiv sein"); return
        result = self.store.apply(SaveTask(TaskDraft(
            title=preview.title, project_id=self._project_ids.get(preview.project), planning_date=preview.planning_date,
            priority=preview.priority, estimated_minutes=preview.estimated_minutes,
        )))
        if result.ok:
            self.saved.emit(result.task_id)
            self.input.clear()
            self.hide()
        else:
            self.preview_label.setText(result.message)


class InboxView(QWidget):
    task_selected = Signal(int)
    def __init__(self, store: TaskStore, parent=None):
        super().__init__(parent)
        self.store = store
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Eingang"))
        self.list = QListWidget()
        self.list.itemClicked.connect(lambda item: self.task_selected.emit(item.data(Qt.UserRole)))
        self.list.itemActivated.connect(lambda item: self.task_selected.emit(item.data(Qt.UserRole)))
        layout.addWidget(self.list, 1)
        store.changed.connect(lambda change: self.refresh() if "tasks" in change.domains else None)
        self.refresh()

    def refresh(self) -> None:
        self.list.clear()
        for summary in self.store.repository.query(QuerySpec(limit=5000)):
            record = self.store.repository.get(summary.id)
            if record and record.draft.status != "Erledigt" and not is_clarified(record.draft):
                item = QListWidgetItem(record.draft.title); item.setData(Qt.UserRole, record.id)
                self.list.addItem(item)

    def titles(self) -> list[str]:
        return [self.list.item(index).text() for index in range(self.list.count())]
