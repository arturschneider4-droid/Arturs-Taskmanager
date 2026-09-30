from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtCore import QObject, QTimer, Signal

from .repositories import TaskRepository
from .task_model import TaskDraft
from .undo import UndoManager


@dataclass(frozen=True)
class ChangeSet:
    task_ids: frozenset[int]
    domains: frozenset[str]


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    task_id: int | None = None
    message: str = ""


class TaskCommand(Protocol):
    def execute(self, repository: TaskRepository) -> CommandResult: ...

    def changes(self, result: CommandResult) -> ChangeSet: ...


@dataclass(frozen=True)
class SaveTask:
    draft: TaskDraft
    task_id: int | None = None

    def execute(self, repository: TaskRepository) -> CommandResult:
        task_id = repository.save(self.draft, self.task_id)
        return CommandResult(True, task_id, "Gespeichert")

    def changes(self, result: CommandResult) -> ChangeSet:
        return ChangeSet(frozenset({result.task_id}), frozenset({"tasks", "dashboard"}))


@dataclass(frozen=True)
class DeleteTask:
    task_id: int
    def execute(self, repository: TaskRepository) -> CommandResult:
        if repository.get(self.task_id) is None:
            return CommandResult(False, self.task_id, "Aufgabe nicht gefunden")
        repository.delete(self.task_id)
        return CommandResult(True, self.task_id, "Gelöscht")
    def changes(self, result: CommandResult) -> ChangeSet:
        return ChangeSet(frozenset({self.task_id}), frozenset({"tasks", "dashboard"}))


class TaskStore(QObject):
    changed = Signal(object)

    def __init__(self, repository: TaskRepository, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.undo_manager = UndoManager(repository)

    def apply(self, command: TaskCommand) -> CommandResult:
        task_id = getattr(command, "task_id", None)
        if task_id is not None:
            self.undo_manager.capture(task_id)
        try:
            result = command.execute(self.repository)
        except (ValueError, OSError) as error:
            return CommandResult(False, message=str(error))
        self.changed.emit(command.changes(result))
        return result

    def undo(self) -> bool:
        if not self.undo_manager.undo():
            return False
        self.changed.emit(ChangeSet(frozenset(), frozenset({"tasks", "dashboard"})))
        return True


class SearchDebouncer(QObject):
    submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pending = ""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(180)
        self._timer.timeout.connect(self._emit_pending)

    def submit(self, text: str) -> None:
        self._pending = text
        self._timer.start()

    def _emit_pending(self) -> None:
        self.submitted.emit(self._pending)
