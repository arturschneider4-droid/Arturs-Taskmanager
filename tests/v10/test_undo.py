from dataclasses import replace
from datetime import date

from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.undo import UndoManager


def test_multiple_undo_steps_restore_edit_move_and_delete(v10_database):
    repository = TaskRepository(v10_database); manager = UndoManager(repository)
    task_id = repository.save(TaskDraft(title="Original"))
    manager.capture(task_id); repository.save(replace(repository.get(task_id).draft, title="Bearbeitet"), task_id)
    manager.capture(task_id); repository.save(replace(repository.get(task_id).draft, planning_date=date(2026, 9, 30)), task_id)
    manager.capture(task_id); repository.delete(task_id)
    assert manager.can_undo
    manager.undo(); assert repository.get(task_id).draft.planning_date == date(2026, 9, 30)
    manager.undo(); assert repository.get(task_id).draft.planning_date is None
    manager.undo(); assert repository.get(task_id).draft.title == "Original"
    assert not manager.can_undo


def test_shell_undo_works_from_dashboard_without_task_selection(qtbot, v10_database):
    from taskmanager.repositories import TaskRepository
    from taskmanager.shortcuts import ShortcutAction
    from taskmanager.task_store import SaveTask, TaskStore
    from taskmanager.v10_shell import V10Shell
    repository = TaskRepository(v10_database); task_id = repository.save(TaskDraft(title="Vorher"))
    store = TaskStore(repository); shell = V10Shell(store); qtbot.addWidget(shell)
    store.apply(SaveTask(replace(repository.get(task_id).draft, title="Nachher"), task_id))
    shell._dispatch_shortcut(ShortcutAction.UNDO)
    assert repository.get(task_id).draft.title == "Vorher"
