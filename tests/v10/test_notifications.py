from datetime import datetime, timedelta

from taskmanager.notifications import ReminderScheduler
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


NOW = datetime(2026, 9, 28, 9, 0)


class FakeBackend:
    def __init__(self, fail=False): self.messages = []; self.fail = fail
    def show(self, title, message):
        if self.fail: raise RuntimeError("Tray nicht verfügbar")
        self.messages.append((title, message))


def test_reminders_are_disabled_by_default(v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Still", reminder_at=NOW) if False else TaskDraft(title="Still"))
    backend = FakeBackend(); scheduler = ReminderScheduler(TaskStore(repository), backend, clock=lambda: NOW)
    assert scheduler.reconcile() == []
    assert backend.messages == []


def test_due_and_missed_reminder_fire_once_on_start(v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Termin", reminder_enabled=True, reminder_at=NOW - timedelta(hours=1), reminder_lead_minutes=30))
    backend = FakeBackend(); scheduler = ReminderScheduler(TaskStore(repository), backend, clock=lambda: NOW)
    scheduler.start(); scheduler.stop()
    assert scheduler.reconcile() == []
    assert backend.messages == [("Arturs Taskmanager", "Termin")]


def test_backend_failure_does_not_block_scheduler_start(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Fehler", reminder_enabled=True, reminder_at=NOW))
    scheduler = ReminderScheduler(TaskStore(repository), FakeBackend(fail=True), clock=lambda: NOW)
    with qtbot.waitSignal(scheduler.feedback) as signal:
        scheduler.start()
    scheduler.stop()
    assert "nicht verfügbar" in signal.args[0]
