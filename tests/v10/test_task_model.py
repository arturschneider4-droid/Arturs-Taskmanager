from datetime import date, datetime

import pytest

from taskmanager.task_model import ControlMode, TaskDraft


def draft(**changes):
    values = {"title": "Angebot freigeben"}
    values.update(changes)
    return TaskDraft(**values)


def test_task_draft_normalizes_title_and_typed_dates():
    item = draft(
        title="  Angebot freigeben  ",
        planning_date=date(2026, 9, 28),
        reminder_enabled=True,
        reminder_at=datetime(2026, 9, 28, 8, 30),
    )
    assert item.title == "Angebot freigeben"
    assert item.planning_date == date(2026, 9, 28)
    assert item.reminder_at == datetime(2026, 9, 28, 8, 30)


def test_task_draft_rejects_blank_title():
    with pytest.raises(ValueError, match="Titel"):
        draft(title="   ")


def test_task_draft_rejects_reminder_time_while_disabled():
    with pytest.raises(ValueError, match="Erinnerung"):
        draft(reminder_enabled=False, reminder_at=datetime(2026, 9, 28, 8, 30))


@pytest.mark.parametrize("mode", [ControlMode.DELEGATED, ControlMode.WAITING])
def test_follow_up_modes_require_a_responsible_party(mode):
    with pytest.raises(ValueError, match="Person oder Organisation"):
        draft(control_mode=mode)


def test_task_draft_exposes_all_v10_planning_and_follow_up_fields():
    item = draft()
    expected = {
        "title", "description", "project_id", "priority", "status", "subtasks",
        "recurrence", "planning_date", "planning_time", "deadline",
        "estimated_minutes", "is_top_three", "reminder_enabled", "reminder_at",
        "reminder_lead_minutes", "control_mode", "responsible_party",
        "delegated_at", "last_contact_at", "expected_response_at", "follow_up_date",
        "people_tags",
    }
    assert set(item.__dataclass_fields__) == expected
