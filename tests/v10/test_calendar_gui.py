from datetime import date

from taskmanager.calendar_view import CalendarView
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


def test_calendar_uses_distinct_planning_and_deadline_semantics(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Termin", planning_date=date(2026, 9, 28), deadline=date(2026, 10, 2)))
    view = CalendarView(TaskStore(repository), today=date(2026, 9, 28))
    qtbot.addWidget(view)
    item = view.item_for(task_id)
    assert item.planning_marker == "●"
    assert item.deadline_marker == "◆"
    assert "Planung" in view.legend_label.text() and "Deadline" in view.legend_label.text()


def test_planning_drop_does_not_change_deadline(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Plan", planning_date=date(2026, 9, 28), deadline=date(2026, 10, 2)))
    view = CalendarView(TaskStore(repository))
    qtbot.addWidget(view)
    assert view.move_planning_date(task_id, date(2026, 9, 30))
    draft = repository.get(task_id).draft
    assert draft.planning_date == date(2026, 9, 30)
    assert draft.deadline == date(2026, 10, 2)


def test_deadline_move_is_separate_explicit_action(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Frist", deadline=date(2026, 10, 2)))
    view = CalendarView(TaskStore(repository))
    qtbot.addWidget(view)
    assert view.deadline_action_label == "Deadline ausdrücklich verschieben"
    assert view.move_deadline_explicitly(task_id, date(2026, 10, 5))
    assert repository.get(task_id).draft.deadline == date(2026, 10, 5)


def test_shell_calendar_route_is_real(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.v10_shell import V10Shell
    shell = V10Shell(TaskStore(TaskRepository(v10_database)))
    qtbot.addWidget(shell)
    assert isinstance(shell.page_for(Route.CALENDAR), CalendarView)
