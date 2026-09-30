from datetime import date, datetime

import pytest

from taskmanager.backup_restore import BackupService
from taskmanager.follow_up import FollowUpService
from taskmanager.quick_capture import parse_capture
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import SaveTask, TaskStore
from taskmanager.weekly_review import WeeklyReviewService


@pytest.mark.parametrize("iteration", range(3))
def test_capture_plan_delegate_followup_review_complete_restart_restore(iteration, v10_database, tmp_path):
    repository = TaskRepository(v10_database); store = TaskStore(repository)
    preview = parse_capture(f"Kernworkflow {iteration} morgen", today=date(2026, 9, 28), projects=[])
    task_id = repository.save(TaskDraft(title=preview.title, planning_date=preview.planning_date))
    followups = FollowUpService(store, clock=lambda: datetime(2026, 9, 28, 9))
    assert followups.delegate(task_id, "Anna", date(2026, 9, 30)).ok
    assert followups.follow_up(task_id, date(2026, 10, 2)).ok
    review = WeeklyReviewService(v10_database, today=date(2026, 9, 28)); review.start()
    backup = BackupService(v10_database, tmp_path / "backups").create("e2e")
    record = repository.get(task_id); store.apply(SaveTask(__import__('dataclasses').replace(record.draft, status="Erledigt"), task_id))
    assert TaskRepository(v10_database).get(task_id).draft.status == "Erledigt"
    BackupService(v10_database, tmp_path / "backups").restore(backup)
    assert TaskRepository(v10_database).get(task_id).draft.status != "Erledigt"
