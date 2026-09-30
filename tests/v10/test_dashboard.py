from datetime import date, datetime
import sqlite3

from taskmanager.dashboard import DashboardService
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import ControlMode, TaskDraft


def test_dashboard_snapshot_contains_all_executive_metrics(v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Heute", planning_date=date(2026, 9, 26), is_top_three=True))
    repository.save(TaskDraft(title="Risiko", deadline=date(2026, 9, 25)))
    repository.save(TaskDraft(title="Delegiert", control_mode=ControlMode.DELEGATED, responsible_party="Anna", delegated_at=datetime(2026, 9, 20, 8)))
    repository.save(TaskDraft(title="Warten", control_mode=ControlMode.WAITING, responsible_party="Kunde", follow_up_date=date(2026, 9, 26)))

    snapshot = DashboardService(v10_database).snapshot(date(2026, 9, 26))

    assert set(snapshot.metric_values) == {
        "today", "overdue", "follow_ups", "delegated", "top_three",
        "critical_deadlines", "unplanned", "week_progress",
    }
    assert snapshot.metric_values["today"] == 1
    assert snapshot.metric_values["overdue"] == 1
    assert snapshot.metric_values["follow_ups"] == 1
    assert snapshot.metric_values["delegated"] == 1


def test_weekly_focus_snapshot_limits_goals_and_selects_critical_items(v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Früheste Deadline", deadline=date(2026, 9, 27)))
    repository.save(TaskDraft(title="Alte Delegation", control_mode=ControlMode.DELEGATED, responsible_party="Anna", delegated_at=datetime(2026, 9, 10, 8)))
    repository.save(TaskDraft(title="Nächste Wiedervorlage", control_mode=ControlMode.WAITING, responsible_party="Kunde", follow_up_date=date(2026, 9, 26)))
    connection = sqlite3.connect(v10_database)
    connection.executemany(
        "INSERT INTO weekly_goals(year,week,title,position,done) VALUES(2026,39,?,?,?)",
        [("Umsatz", 1, 1), ("Team", 2, 0), ("Labor", 3, 0)],
    )
    connection.commit()
    connection.close()

    focus = DashboardService(v10_database).weekly_focus(date(2026, 9, 26))

    assert [goal.title for goal in focus.goals] == ["Umsatz", "Team", "Labor"]
    assert focus.next_deadline == "Früheste Deadline"
    assert focus.oldest_delegation == "Alte Delegation"
    assert focus.next_follow_up == "Nächste Wiedervorlage"
    assert focus.progress_percent == 33
