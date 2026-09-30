from datetime import datetime, timedelta

from taskmanager.notifications import DueReminderDialog
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


NOW = datetime(2026, 9, 28, 9, 0)


def test_due_dialog_can_complete_task(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Fertig"))
    dialog = DueReminderDialog(TaskStore(repository), task_id, clock=lambda: NOW)
    qtbot.addWidget(dialog)
    dialog.complete_button.click()
    assert repository.get(task_id).draft.status == "Erledigt"


def test_due_dialog_can_snooze_individually(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Später", reminder_enabled=True, reminder_at=NOW))
    dialog = DueReminderDialog(TaskStore(repository), task_id, clock=lambda: NOW)
    qtbot.addWidget(dialog)
    dialog.snooze_minutes.setValue(45)
    dialog.snooze_button.click()
    assert repository.get(task_id).draft.reminder_at == NOW + timedelta(minutes=45)
