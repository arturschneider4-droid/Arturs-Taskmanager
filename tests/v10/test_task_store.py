from datetime import date

from taskmanager.repositories import DashboardRepository, QuerySpec, TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import SaveTask, SearchDebouncer, TaskStore


def migrated_repository(tmp_path):
    from taskmanager.migrations import migrate_to_v10
    from tests.v10.test_migrations import make_legacy_database

    path = tmp_path / "tasks.db"
    make_legacy_database(path)
    migrate_to_v10(path, tmp_path / "backups")
    return TaskRepository(path), path


def test_store_emits_exactly_one_targeted_change_for_save(qtbot, tmp_path):
    repository, _ = migrated_repository(tmp_path)
    store = TaskStore(repository)
    with qtbot.waitSignal(store.changed) as signal:
        result = store.apply(SaveTask(TaskDraft(title="Entscheidung vorbereiten")))
    assert result.ok is True
    assert signal.args[0].task_ids == frozenset({result.task_id})
    assert signal.args[0].domains == frozenset({"tasks", "dashboard"})


def test_query_spec_filters_search_planning_and_control_mode(tmp_path):
    repository, _ = migrated_repository(tmp_path)
    repository.save(TaskDraft(title="Budget Labor", planning_date=date(2026, 9, 29)))
    repository.save(TaskDraft(title="Privater Einkauf", planning_date=date(2026, 10, 5)))
    rows = repository.query(QuerySpec(search="labor", planned_from=date(2026, 9, 28), planned_to=date(2026, 10, 1)))
    assert [row.title for row in rows] == ["Budget Labor"]


def test_dashboard_metrics_are_calculated_in_one_repository_call(tmp_path):
    repository, path = migrated_repository(tmp_path)
    repository.save(TaskDraft(title="Heute", planning_date=date(2026, 9, 26)))
    repository.save(TaskDraft(title="Überfällig", deadline=date(2026, 9, 25)))
    metrics = DashboardRepository(path).metrics(date(2026, 9, 26))
    assert metrics.today_open == 1
    assert metrics.overdue == 1
    assert metrics.unplanned >= 1


def test_search_debouncer_emits_only_the_latest_rapid_input(qtbot):
    debouncer = SearchDebouncer()
    with qtbot.waitSignal(debouncer.submitted, timeout=500) as signal:
        debouncer.submit("lab")
        debouncer.submit("labor")
    assert signal.args == ["labor"]
