from dataclasses import replace
from datetime import datetime, timedelta
import sqlite3

from PySide6.QtCore import Qt

from taskmanager.board_views import KanbanView
from taskmanager.migrations import migrate_to_v10
from taskmanager.repositories import QuerySpec, TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import SaveTask, TaskStore


def completed_at(repository, task_id, when):
    with sqlite3.connect(repository.db_path) as connection:
        connection.execute("UPDATE tasks SET completed_at=? WHERE id=?", (when.isoformat(), task_id))


def test_completion_clock_survives_edits_and_resets_on_reopening(v10_database):
    repo = TaskRepository(v10_database)
    task_id = repo.save(TaskDraft(title="Prüfbericht"))
    assert repo.get(task_id).completed_at is None
    repo.save(replace(repo.get(task_id).draft, status="Erledigt"), task_id)
    assert repo.get(task_id).completed_at is not None
    completed_at(repo, task_id, datetime(2026, 9, 20, 10))
    repo.save(replace(repo.get(task_id).draft, title="Prüfbericht aktualisiert"), task_id)
    assert repo.get(task_id).completed_at == datetime(2026, 9, 20, 10)
    repo.save(replace(repo.get(task_id).draft, status="Offen"), task_id)
    assert repo.get(task_id).completed_at is None
    repo.save(replace(repo.get(task_id).draft, status="Erledigt"), task_id)
    assert repo.get(task_id).completed_at > datetime(2026, 9, 20, 10)


def test_archive_exact_seven_day_boundary_preserves_data(v10_database):
    repo = TaskRepository(v10_database)
    due = repo.save(TaskDraft(title="Fällig", status="Erledigt", description="Behalten", subtasks=(("Teil", True),)))
    fresh = repo.save(TaskDraft(title="Noch frisch", status="Erledigt"))
    active = repo.save(TaskDraft(title="Offen"))
    completed_at(repo, due, datetime(2026, 9, 28, 10))
    completed_at(repo, fresh, datetime(2026, 9, 28, 10, 0, 1))
    updated = repo.get(due).updated_at
    assert repo.archive_completed(datetime(2026, 10, 5, 10)) == frozenset({due})
    assert {t.id for t in repo.query()} == {fresh, active}
    assert [t.id for t in repo.query(QuerySpec(archived=True))] == [due]
    record = repo.get(due)
    assert record.draft.status == "Erledigt"
    assert record.draft.description == "Behalten" and record.draft.subtasks == (("Teil", True),)
    assert record.updated_at == updated
    assert repo.archive_completed(datetime(2026, 10, 5, 10)) == frozenset()
    # An ordinary edit must not silently unarchive a completed task.
    repo.save(replace(record.draft, title="Archiv bearbeitet"), due)
    assert repo.get(due).archived_at is not None


def test_store_archives_on_startup_and_timer_refreshes_board(qtbot, v10_database):
    repo = TaskRepository(v10_database)
    old = repo.save(TaskDraft(title="Alt", status="Erledigt"))
    completed_at(repo, old, datetime.now() - timedelta(days=8))
    store = TaskStore(repo)
    assert repo.get(old).archived_at is not None
    view = KanbanView(store); qtbot.addWidget(view); view.show()
    assert view.lane_widgets["Archivierte Aufgaben"].count() == 1
    assert not view.lane_widgets["Archivierte Aufgaben"].isVisible()
    qtbot.mouseClick(view.archive_toggle, Qt.LeftButton)
    assert view.lane_widgets["Archivierte Aufgaben"].isVisible()
    task_id = repo.save(TaskDraft(title="Nachträglich fällig", status="Erledigt"))
    completed_at(repo, task_id, datetime.now() - timedelta(days=8))
    store.archive_timer.setInterval(10)
    qtbot.waitUntil(lambda: view.lane_widgets["Archivierte Aufgaben"].count() == 2)
    assert view.move_task(old, "Offen")
    assert repo.get(old).archived_at is None
    assert repo.get(old).completed_at is None
    assert view.lane_widgets["Offen"].count() == 1
    assert store.undo()
    assert repo.get(old).archived_at is not None
    assert view.lane_widgets["Archivierte Aufgaben"].count() == 2


def test_archive_keeps_query_filters_and_does_not_consume_active_limit(qtbot, v10_database):
    repo = TaskRepository(v10_database)
    old = repo.save(TaskDraft(title="Alpha alt", status="Erledigt"))
    completed_at(repo, old, datetime.now() - timedelta(days=8))
    repo.save(TaskDraft(title="Alpha offen"))
    repo.save(TaskDraft(title="Beta"))
    view = KanbanView(TaskStore(repo)); qtbot.addWidget(view)
    view.set_query(QuerySpec(search="Alpha", limit=1))
    assert set(view.titles()) == {"Alpha alt", "Alpha offen"}
    assert view.move_task(old, "Archivierte Aufgaben") is False


def test_recurring_successor_has_no_completion_or_archive_date(v10_database):
    repo = TaskRepository(v10_database)
    task_id = repo.save(TaskDraft(title="Wiederkehrend", recurrence="weekly"))
    repo.save(replace(repo.get(task_id).draft, status="Erledigt"), task_id)
    successor = repo.get(repo.last_created_recurrence_id)
    assert successor.completed_at is None and successor.archived_at is None


def test_existing_v10_database_upgrades_and_preserves_completion_on_repeat(v10_database, monkeypatch):
    from taskmanager import app
    with sqlite3.connect(v10_database) as connection:
        columns = {r[1] for r in connection.execute("PRAGMA table_info(tasks)")}
        for column in ("completed_at", "archived_at"):
            if column in columns:
                connection.execute(f"ALTER TABLE tasks DROP COLUMN {column}")
        connection.execute("INSERT INTO tasks(title,status,created_at,updated_at) VALUES('Alt','Erledigt','2026-09-01T10:00:00','2026-09-20T10:00:00')")
    monkeypatch.setattr(app, "DB_PATH", v10_database)
    app._ensure_v10_schema()
    repo = TaskRepository(v10_database)
    record = repo.get(1)
    assert record.completed_at == datetime(2026, 9, 20, 10)
    repo.save(replace(record.draft, title="Bearbeitet"), record.id)
    migrate_to_v10(v10_database, v10_database.parent / "backups")
    assert repo.get(record.id).completed_at == datetime(2026, 9, 20, 10)
