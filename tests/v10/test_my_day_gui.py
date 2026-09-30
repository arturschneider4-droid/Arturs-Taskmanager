from datetime import date, timedelta

from taskmanager.repositories import TaskRepository
from taskmanager.task_list import MyDayView, NextSevenDaysView
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


TODAY = date(2026, 9, 28)


def test_my_day_groups_top_three_today_overdue_and_followups(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Top-Ziel", planning_date=TODAY, is_top_three=True))
    repository.save(TaskDraft(title="Heute", planning_date=TODAY))
    repository.save(TaskDraft(title="Überfällig", planning_date=TODAY - timedelta(days=1)))
    repository.save(TaskDraft(title="Nachfassen", responsible_party="Anna", control_mode="waiting", follow_up_date=TODAY))
    view = MyDayView(TaskStore(repository), today=TODAY)
    qtbot.addWidget(view)
    assert view.group_titles() == {
        "Top 3": ["Top-Ziel"],
        "Heute geplant": ["Heute"],
        "Überfällig": ["Überfällig"],
        "Heute nachfassen": ["Nachfassen"],
    }


def test_top_three_fourth_task_requires_and_performs_atomic_replacement(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    ids = [repository.save(TaskDraft(title=f"Top {n}", is_top_three=True)) for n in range(1, 4)]
    fourth = repository.save(TaskDraft(title="Kandidat"))
    view = MyDayView(TaskStore(repository), today=TODAY)
    qtbot.addWidget(view)
    assert view.promote_to_top_three(fourth) is False
    assert view.pending_replacement_task_id == fourth
    assert view.replace_top_three(ids[0]) is True
    assert repository.get(ids[0]).draft.is_top_three is False
    assert repository.get(fourth).draft.is_top_three is True


def test_next_seven_days_groups_by_planning_date_and_keeps_deadline_separate(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Termin", planning_date=TODAY + timedelta(days=1), deadline=TODAY + timedelta(days=4)))
    view = NextSevenDaysView(TaskStore(repository), today=TODAY)
    qtbot.addWidget(view)
    assert view.group_titles()["Di., 29.09."] == ["Termin"]
    row = view.row_for_title("Termin")
    assert row.planning_label.text() == "Geplant: 29.09.2026"
    assert row.deadline_label.text() == "Frist: 02.10.2026"


def test_shell_uses_real_planning_pages_and_opens_selected_task(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.v10_shell import V10Shell

    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Öffnen", planning_date=TODAY))
    shell = V10Shell(TaskStore(repository))
    qtbot.addWidget(shell)
    assert isinstance(shell.page_for(Route.MY_DAY), MyDayView)
    assert isinstance(shell.page_for(Route.NEXT_SEVEN), NextSevenDaysView)
    shell.page_for(Route.MY_DAY).select_task(task_id)
    assert shell.detail_panel.task_id == task_id
