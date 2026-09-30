from datetime import date, timedelta

import pytest

from taskmanager.repositories import QuerySpec, TaskRepository
from taskmanager.task_list import RowAction, TaskListView
from taskmanager.task_model import ControlMode, TaskDraft
from taskmanager.task_store import TaskStore


TODAY = date(2026, 9, 28)


@pytest.mark.parametrize("action", list(RowAction))
def test_each_row_action_is_functional(qtbot, v10_database, action):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Aktion"))
    view = TaskListView(TaskStore(repository), today=TODAY)
    qtbot.addWidget(view)
    with qtbot.waitSignal(view.action_performed) as signal:
        view.perform_action(task_id, action)
    assert signal.args == [task_id, action]
    task = repository.get(task_id)
    if action is RowAction.TODAY:
        assert task.draft.planning_date == TODAY
    elif action is RowAction.TOMORROW:
        assert task.draft.planning_date == TODAY + timedelta(days=1)
    elif action is RowAction.COMPLETE:
        assert task.draft.status == "Erledigt"
    elif action is RowAction.DELEGATE:
        assert view.pending_editor == (task_id, ControlMode.DELEGATED)
    elif action is RowAction.WAIT:
        assert view.pending_editor == (task_id, ControlMode.WAITING)
    elif action is RowAction.MORE:
        assert view.more_menu_for(task_id) is not None


def test_query_selection_and_scroll_survive_targeted_refresh(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    ids = [repository.save(TaskDraft(title=f"Aufgabe {n}")) for n in range(30)]
    store = TaskStore(repository)
    view = TaskListView(store, today=TODAY)
    qtbot.addWidget(view)
    view.resize(700, 300)
    view.show()
    view.set_query(QuerySpec(search="Aufgabe"))
    view.select_task(ids[12])
    view.scroll_area.verticalScrollBar().setValue(120)
    before = view.scroll_area.verticalScrollBar().value()
    view.refresh()
    assert view.selected_task_id == ids[12]
    assert view.scroll_area.verticalScrollBar().value() == before
