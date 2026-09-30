from datetime import date

import pytest

from taskmanager.weekly_review import REVIEW_STEPS, WeeklyReviewService


TODAY = date(2026, 9, 28)


def test_review_has_seven_steps_and_resumes_persisted_progress(v10_database):
    service = WeeklyReviewService(v10_database, today=TODAY)
    session = service.start()
    assert len(REVIEW_STEPS) == 7
    assert session.current_step == 1
    service.advance({"inbox": "done"})
    resumed = WeeklyReviewService(v10_database, today=TODAY).resume()
    assert resumed.current_step == 2
    assert resumed.answers["inbox"] == "done"


def test_review_can_move_back_without_losing_answers(v10_database):
    service = WeeklyReviewService(v10_database, today=TODAY)
    service.start()
    service.advance({"one": 1})
    service.back()
    assert service.resume().current_step == 1
    assert service.resume().answers["one"] == 1


def test_weekly_goals_are_limited_to_three(v10_database):
    service = WeeklyReviewService(v10_database, today=TODAY)
    with pytest.raises(ValueError, match="drei"):
        service.set_goals(["A", "B", "C", "D"])
    service.set_goals(["A", "B", "C"])
    assert service.goals() == ["A", "B", "C"]


def test_completion_returns_correct_summary(v10_database):
    service = WeeklyReviewService(v10_database, today=TODAY)
    service.start()
    service.set_goals(["Umsatz", "Team"])
    for index in range(6):
        service.advance({f"step_{index}": True})
    summary = service.complete()
    assert summary.steps_completed == 7
    assert summary.goals == ("Umsatz", "Team")
    assert service.resume().completed_at is not None
