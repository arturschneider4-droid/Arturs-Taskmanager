from datetime import date

import pytest

from taskmanager.dashboard import DashboardFilter, ExecutiveDashboard, WeeklyFocusPanel
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


@pytest.mark.parametrize("filter_key", list(DashboardFilter))
def test_every_dashboard_card_opens_its_exact_filter(qtbot, v10_database, filter_key):
    store = TaskStore(TaskRepository(v10_database))
    dashboard = ExecutiveDashboard(store, today=date(2026, 9, 26))
    qtbot.addWidget(dashboard)
    card = dashboard.card_for(filter_key)
    with qtbot.waitSignal(dashboard.filter_requested) as signal:
        qtbot.mouseClick(card, __import__("PySide6").QtCore.Qt.MouseButton.LeftButton)
    assert signal.args == [filter_key]
    assert card.accessibleName().startswith(filter_key.label + ":")


def test_dashboard_refreshes_only_for_dashboard_change_domain(qtbot, v10_database):
    store = TaskStore(TaskRepository(v10_database))
    dashboard = ExecutiveDashboard(store, today=date(2026, 9, 26))
    qtbot.addWidget(dashboard)
    initial = dashboard.refresh_count
    store.changed.emit(__import__("taskmanager.task_store", fromlist=["ChangeSet"]).ChangeSet(frozenset({1}), frozenset({"tasks"})))
    assert dashboard.refresh_count == initial
    store.changed.emit(__import__("taskmanager.task_store", fromlist=["ChangeSet"]).ChangeSet(frozenset({1}), frozenset({"dashboard"})))
    assert dashboard.refresh_count == initial + 1


def test_weekly_focus_review_action_is_real(qtbot, v10_database):
    store = TaskStore(TaskRepository(v10_database))
    panel = WeeklyFocusPanel(store, today=date(2026, 9, 26))
    qtbot.addWidget(panel)
    with qtbot.waitSignal(panel.review_requested):
        qtbot.mouseClick(panel.review_button, __import__("PySide6").QtCore.Qt.MouseButton.LeftButton)


def test_shell_uses_real_dashboard_and_routes_every_metric(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.v10_shell import V10Shell

    store = TaskStore(TaskRepository(v10_database))
    shell = V10Shell(store)
    qtbot.addWidget(shell)
    assert isinstance(shell.page_for(Route.DASHBOARD), ExecutiveDashboard)
    assert isinstance(shell.weekly_focus, WeeklyFocusPanel)
    expected_routes = {
        DashboardFilter.TODAY: Route.MY_DAY,
        DashboardFilter.OVERDUE: Route.TASKS,
        DashboardFilter.FOLLOW_UPS: Route.WAITING,
        DashboardFilter.DELEGATED: Route.DELEGATED,
        DashboardFilter.TOP_THREE: Route.MY_DAY,
        DashboardFilter.CRITICAL_DEADLINES: Route.TASKS,
        DashboardFilter.UNPLANNED: Route.TASKS,
        DashboardFilter.WEEK_PROGRESS: Route.TASKS,
    }
    dashboard = shell.page_for(Route.DASHBOARD)
    for dashboard_filter, route in expected_routes.items():
        dashboard.card_for(dashboard_filter).click()
        assert shell.active_dashboard_filter is dashboard_filter
        assert shell.current_route is route
