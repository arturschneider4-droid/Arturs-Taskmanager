from taskmanager.board_views import EisenhowerView, KanbanView
from taskmanager.repositories import QuerySpec, TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


def test_kanban_moves_status_and_preserves_top_three(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Board", is_top_three=True))
    view = KanbanView(TaskStore(repository))
    qtbot.addWidget(view)
    assert view.move_task(task_id, "In Arbeit")
    draft = repository.get(task_id).draft
    assert draft.status == "In Arbeit"
    assert draft.is_top_three is True


def test_eisenhower_moves_priority_and_rejects_invalid_drop(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Matrix"))
    view = EisenhowerView(TaskStore(repository))
    qtbot.addWidget(view)
    assert view.move_task(task_id, "important_urgent")
    assert repository.get(task_id).draft.priority == "important_urgent"
    assert view.move_task(task_id, "unbekannt") is False
    assert repository.get(task_id).draft.priority == "important_urgent"


def test_boards_share_query_filter(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Alpha"))
    repository.save(TaskDraft(title="Beta"))
    for view_type in (KanbanView, EisenhowerView):
        view = view_type(TaskStore(repository))
        qtbot.addWidget(view)
        view.set_query(QuerySpec(search="Alpha"))
        assert view.titles() == ["Alpha"]


def test_shell_routes_use_real_boards(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.v10_shell import V10Shell
    shell = V10Shell(TaskStore(TaskRepository(v10_database)))
    qtbot.addWidget(shell)
    assert isinstance(shell.page_for(Route.KANBAN), KanbanView)
    assert isinstance(shell.page_for(Route.EISENHOWER), EisenhowerView)
