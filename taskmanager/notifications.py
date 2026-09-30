from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
import sqlite3

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QSpinBox, QSystemTrayIcon, QVBoxLayout

from .task_store import SaveTask, TaskStore


class NotificationBackend:
    def __init__(self, tray_icon: QSystemTrayIcon): self.tray_icon = tray_icon
    def show(self, title: str, message: str): self.tray_icon.showMessage(title, message)


class ReminderScheduler(QObject):
    feedback = Signal(str)
    reminder_due = Signal(int)

    def __init__(self, store: TaskStore, backend: NotificationBackend, clock=datetime.now, parent=None):
        super().__init__(parent); self.store = store; self.backend = backend; self.clock = clock
        self._delivered = set()
        self.timer = QTimer(self); self.timer.setInterval(30_000); self.timer.timeout.connect(self.reconcile)

    def start(self):
        self.reconcile(); self.timer.start()

    def stop(self): self.timer.stop()

    def reconcile(self):
        now = self.clock()
        connection = sqlite3.connect(self.store.repository.db_path)
        rows = connection.execute(
            "SELECT id,title,reminder_at FROM tasks WHERE reminder_enabled=1 AND reminder_at IS NOT NULL AND reminder_at<=? AND status!='Erledigt'",
            (now.isoformat(),),
        ).fetchall(); connection.close()
        delivered = []
        for task_id, title, reminder_at in rows:
            token = (task_id, reminder_at)
            if token in self._delivered: continue
            try:
                self.backend.show("Arturs Taskmanager", title)
            except Exception as error:
                self.feedback.emit(f"Benachrichtigung nicht verfügbar: {error}")
            self._delivered.add(token); delivered.append(task_id); self.reminder_due.emit(task_id)
        return delivered


class DueReminderDialog(QDialog):
    def __init__(self, store: TaskStore, task_id: int, clock=datetime.now, parent=None):
        super().__init__(parent); self.store = store; self.task_id = task_id; self.clock = clock
        record = store.repository.get(task_id)
        root = QVBoxLayout(self)
        root.addWidget(QLabel(record.draft.title if record else "Erinnerung"))
        self.snooze_minutes = QSpinBox(); self.snooze_minutes.setRange(5, 1440); self.snooze_minutes.setValue(30)
        self.snooze_button = QPushButton("Verschieben")
        self.complete_button = QPushButton("Erledigen")
        root.addWidget(self.snooze_minutes); root.addWidget(self.snooze_button); root.addWidget(self.complete_button)
        self.snooze_button.clicked.connect(self._snooze); self.complete_button.clicked.connect(self._complete)

    def _snooze(self):
        record = self.store.repository.get(self.task_id)
        if record:
            self.store.apply(SaveTask(replace(record.draft, reminder_enabled=True, reminder_at=self.clock() + timedelta(minutes=self.snooze_minutes.value())), self.task_id))
        self.accept()

    def _complete(self):
        record = self.store.repository.get(self.task_id)
        if record:
            self.store.apply(SaveTask(replace(record.draft, status="Erledigt", is_top_three=False, reminder_enabled=False, reminder_at=None), self.task_id))
        self.accept()
