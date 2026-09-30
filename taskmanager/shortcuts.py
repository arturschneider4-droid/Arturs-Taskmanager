from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QFrame, QLineEdit, QListWidget, QTextEdit, QVBoxLayout

from .repositories import QuerySpec


class ShortcutAction(str, Enum):
    QUICK_CAPTURE = "quick_capture"
    COMMAND_SEARCH = "command_search"
    NEW_TASK = "new_task"
    TODAY = "today"
    TOMORROW = "tomorrow"
    DELEGATE = "delegate"
    WAIT = "wait"
    PRIORITY_1 = "priority_1"
    PRIORITY_2 = "priority_2"
    PRIORITY_3 = "priority_3"
    PRIORITY_4 = "priority_4"
    COMPLETE = "complete"
    DELETE = "delete"
    UNDO = "undo"


class ShortcutController(QObject):
    dispatched = Signal(object)

    def __init__(self, host, parent=None):
        super().__init__(parent or host)
        self.host = host
        keys = {
            ShortcutAction.QUICK_CAPTURE: "Ctrl+Space", ShortcutAction.COMMAND_SEARCH: "Ctrl+K",
            ShortcutAction.NEW_TASK: "N", ShortcutAction.TODAY: "T", ShortcutAction.TOMORROW: "M",
            ShortcutAction.DELEGATE: "D", ShortcutAction.WAIT: "W",
            ShortcutAction.PRIORITY_1: "1", ShortcutAction.PRIORITY_2: "2",
            ShortcutAction.PRIORITY_3: "3", ShortcutAction.PRIORITY_4: "4",
            ShortcutAction.COMPLETE: "Space", ShortcutAction.DELETE: "Delete", ShortcutAction.UNDO: "Ctrl+Z",
        }
        self.shortcuts = {}
        for action, sequence in keys.items():
            shortcut = QShortcut(QKeySequence(sequence), host)
            shortcut.activated.connect(lambda a=action: self.dispatch(a))
            self.shortcuts[action] = shortcut

    def dispatch(self, action: ShortcutAction) -> bool:
        focus = QApplication.focusWidget()
        if isinstance(focus, (QLineEdit, QTextEdit)):
            return False
        self.dispatched.emit(ShortcutAction(action))
        return True


class CommandSearchOverlay(QFrame):
    task_selected = Signal(int)
    def __init__(self, store, parent=None):
        super().__init__(parent); self.store = store; self.setObjectName("commandSearchOverlay")
        root = QVBoxLayout(self); self.input = QLineEdit(); self.input.setPlaceholderText("Aufgaben und Befehle durchsuchen …")
        self.results = QListWidget(); root.addWidget(self.input); root.addWidget(self.results)
        self.input.textChanged.connect(self.refresh); self.results.itemActivated.connect(lambda item: self.task_selected.emit(item.data(256)))
    def refresh(self, text=""):
        self.results.clear()
        for task in self.store.repository.query(QuerySpec(search=text, limit=50)):
            self.results.addItem(task.title); self.results.item(self.results.count() - 1).setData(256, task.id)
    def open(self):
        self.refresh(self.input.text()); self.show(); self.raise_(); self.input.setFocus()
