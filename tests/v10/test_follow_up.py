from datetime import date, datetime, timedelta

import pytest

from taskmanager.follow_up import FollowUpService
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import ControlMode, TaskDraft
from taskmanager.task_store import TaskStore


NOW = datetime(2026, 9, 28, 9, 0)


def test_delegation_changes_control_not_work_status(v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Angebot", status="In Arbeit"))
    service = FollowUpService(TaskStore(repository), clock=lambda: NOW)
    result = service.delegate(task_id, "Anna", date(2026, 10, 1))
    assert result.ok
    draft = repository.get(task_id).draft
    assert draft.status == "In Arbeit"
    assert draft.control_mode is ControlMode.DELEGATED
    assert draft.responsible_party == "Anna"
    assert draft.delegated_at == NOW


@pytest.mark.parametrize("method", ["delegate", "wait"])
def test_person_and_follow_up_are_required(v10_database, method):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Pflichtfelder"))
    service = FollowUpService(TaskStore(repository), clock=lambda: NOW)
    assert not getattr(service, method)(task_id, "", None).ok


def test_waiting_age_overdue_followup_and_atomic_contact_update(v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Antwort"))
    service = FollowUpService(TaskStore(repository), clock=lambda: NOW)
    service.wait(task_id, "Bank", date(2026, 9, 27))
    item = service.item(task_id, today=NOW.date())
    assert item.waiting_days == 0
    assert item.overdue is True
    assert service.follow_up(task_id, date(2026, 10, 2)).ok
    draft = repository.get(task_id).draft
    assert draft.last_contact_at == NOW
    assert draft.follow_up_date == date(2026, 10, 2)


def test_reclaim_returns_task_to_self_control(v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Rücknahme"))
    service = FollowUpService(TaskStore(repository), clock=lambda: NOW)
    service.delegate(task_id, "Lea", NOW.date() + timedelta(days=2))
    assert service.reclaim(task_id).ok
    draft = repository.get(task_id).draft
    assert draft.control_mode is ControlMode.SELF
    assert draft.responsible_party is None
    assert draft.follow_up_date is None
