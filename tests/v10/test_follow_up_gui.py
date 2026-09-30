from datetime import date, datetime

import pytest

from taskmanager.follow_up import DelegatedView, FollowUpService, PeopleAgendaView, WaitingView
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


NOW = datetime(2026, 9, 28, 9, 0)


@pytest.fixture
def followups(v10_database):
    repository = TaskRepository(v10_database)
    service = FollowUpService(TaskStore(repository), clock=lambda: NOW)
    first = repository.save(TaskDraft(title="Budget"))
    second = repository.save(TaskDraft(title="Vertrag"))
    service.delegate(first, "Anna", date(2026, 9, 29))
    service.wait(second, "Anna", date(2026, 9, 27))
    return service, first, second


@pytest.mark.parametrize("view_type", [WaitingView, DelegatedView, PeopleAgendaView])
def test_follow_up_views_show_required_columns_and_group_by_person(qtbot, followups, view_type):
    service, _first, _second = followups
    view = view_type(service, today=NOW.date())
    qtbot.addWidget(view)
    assert "Anna" in view.people()
    assert set(view.column_names()) >= {"Aufgabe", "Person", "Wartezeit", "Wiedervorlage"}


def test_quick_follow_up_updates_contact_and_requests_next_date(qtbot, followups):
    service, first, _second = followups
    view = DelegatedView(service, today=NOW.date())
    qtbot.addWidget(view)
    with qtbot.waitSignal(view.next_follow_up_requested) as signal:
        view.follow_up_now(first)
    assert signal.args == [first]
    assert service.repository.get(first).draft.last_contact_at == NOW


def test_people_agenda_accepts_new_talking_point(qtbot, followups):
    service, _first, _second = followups
    view = PeopleAgendaView(service, today=NOW.date())
    qtbot.addWidget(view)
    task_id = view.add_talking_point("Anna", "Zielbild abstimmen")
    record = service.repository.get(task_id)
    assert record.draft.responsible_party == "Anna"
    assert record.draft.title == "Zielbild abstimmen"


def test_shell_uses_real_waiting_and_delegated_views(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.v10_shell import V10Shell

    shell = V10Shell(TaskStore(TaskRepository(v10_database)))
    qtbot.addWidget(shell)
    assert isinstance(shell.page_for(Route.WAITING), WaitingView)
    assert isinstance(shell.page_for(Route.DELEGATED), DelegatedView)


def test_task_delegate_action_opens_required_fields_and_saves(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.task_list import RowAction
    from taskmanager.v10_shell import V10Shell
    repository = TaskRepository(v10_database); task_id = repository.save(TaskDraft(title="Übergeben"))
    shell = V10Shell(TaskStore(repository)); qtbot.addWidget(shell); shell.show(); shell.navigate(Route.TASKS)
    shell.page_for(Route.TASKS).perform_action(task_id, RowAction.DELEGATE)
    dialog = shell.assignment_dialog
    assert dialog.isVisible()
    dialog.person_edit.setText("Anna"); dialog.follow_up_edit.setDate(__import__('PySide6').QtCore.QDate(2026, 10, 2)); dialog.save_button.click()
    assert repository.get(task_id).draft.responsible_party == "Anna"
