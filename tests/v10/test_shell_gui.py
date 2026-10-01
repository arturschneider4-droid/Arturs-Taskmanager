import pytest

from taskmanager.navigation import Route
from taskmanager.v10_shell import LayoutMode, V10Shell


@pytest.fixture
def shell(qtbot, v10_database):
    from taskmanager.repositories import TaskRepository
    from taskmanager.task_store import TaskStore

    widget = V10Shell(TaskStore(TaskRepository(v10_database)))
    qtbot.addWidget(widget)
    widget.show()
    return widget


def test_every_primary_route_is_real_and_marks_navigation_active(shell):
    for route in Route:
        shell.navigate(route)
        assert shell.current_route is route
        assert shell.pages.currentWidget() is shell.page_for(route)
        assert shell.navigation.button_for(route).property("active") is True


@pytest.mark.parametrize(
    "width,expected",
    [(1440, LayoutMode.WIDE), (1100, LayoutMode.COMPACT), (760, LayoutMode.OVERLAY)],
)
def test_shell_adapts_without_losing_current_route(shell, qtbot, width, expected):
    shell.navigate(Route.INBOX)
    shell.resize(width, 800)
    qtbot.waitUntil(lambda: shell.layout_mode is expected)
    assert shell.current_route is Route.INBOX
    assert shell.pages.currentWidget() is shell.page_for(Route.INBOX)


def test_closing_task_restores_weekly_focus(shell, qtbot):
    shell.detail_panel.open_task(1)
    assert shell.context_stack.currentWidget() is shell.detail_panel
    shell.detail_panel.close_requested.emit()
    qtbot.waitUntil(lambda: shell.context_stack.currentWidget() is shell.weekly_focus)


def test_navigation_does_not_rebuild_page_or_reset_scroll(shell, qtbot):
    from taskmanager.task_model import TaskDraft
    for i in range(30): shell.store.repository.save(TaskDraft(title=f"Aufgabe {i}"))
    shell.navigate(Route.TASKS)
    tasks = shell.page_for(Route.TASKS)
    qtbot.waitUntil(lambda: tasks.scroll_area.verticalScrollBar().maximum() > 37)
    tasks.scroll_area.verticalScrollBar().setValue(37)
    identity = id(tasks)
    shell.navigate(Route.INBOX)
    shell.navigate(Route.TASKS)
    assert id(shell.page_for(Route.TASKS)) == identity
    assert tasks.scroll_area.verticalScrollBar().value() == 37


def test_application_factory_uses_v10_shell_as_production_window(qtbot, v10_database):
    from taskmanager.app import create_v10_window

    window = create_v10_window(v10_database)
    qtbot.addWidget(window)
    assert isinstance(window, V10Shell)
    assert window.windowTitle() == "Arturs Taskmanager V10.0"
