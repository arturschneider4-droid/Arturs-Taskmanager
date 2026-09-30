from pathlib import Path
import hashlib
import sqlite3

import pytest

from taskmanager.migrations import MigrationError, migrate_to_v10
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft


FIXTURE = Path(__file__).parent / "fixtures" / "v92_representative.sql"


def make_legacy_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(FIXTURE.read_text(encoding="utf-8"))
    connection.close()


def legacy_fingerprint(path: Path):
    connection = sqlite3.connect(path)
    result = tuple(connection.execute(
        "SELECT id,title,description,project_id,priority,due_date,status,recurrence,created_at,updated_at FROM tasks ORDER BY id"
    ))
    connection.close()
    return hashlib.sha256(repr(result).encode()).hexdigest()


def test_migration_preserves_v92_data_and_maps_due_date_to_deadline(tmp_path):
    db_path = tmp_path / "tasks.db"
    backup_dir = tmp_path / "backups"
    make_legacy_database(db_path)
    before = legacy_fingerprint(db_path)

    result = migrate_to_v10(db_path, backup_dir)

    assert result.from_version == 9
    assert result.to_version == 10
    assert result.backup_path.exists()
    assert legacy_fingerprint(result.backup_path) == before
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    task = connection.execute("SELECT * FROM tasks WHERE id=1").fetchone()
    assert task["deadline"] == "2026-10-02"
    assert task["due_date"] == "2026-10-02"
    assert task["control_mode"] == "self"
    assert task["reminder_enabled"] == 0
    assert connection.execute("SELECT COUNT(*) FROM subtasks WHERE task_id=1").fetchone()[0] == 1
    assert connection.execute("SELECT status FROM tasks WHERE id=2").fetchone()[0] == "Erledigt"
    connection.close()


def test_migration_creates_v10_support_tables_and_indexes(tmp_path):
    db_path = tmp_path / "tasks.db"
    make_legacy_database(db_path)
    migrate_to_v10(db_path, tmp_path / "backups")
    connection = sqlite3.connect(db_path)
    names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    assert {"schema_versions", "weekly_goals", "review_sessions", "task_people", "undo_log"} <= names
    assert {"idx_tasks_planning_date", "idx_tasks_deadline", "idx_tasks_follow_up_date", "idx_tasks_control_mode"} <= names
    connection.close()


def test_migration_rolls_back_when_integrity_check_fails(tmp_path, monkeypatch):
    db_path = tmp_path / "tasks.db"
    make_legacy_database(db_path)
    before = db_path.read_bytes()
    monkeypatch.setattr("taskmanager.migrations._validate_v10", lambda _connection: (_ for _ in ()).throw(MigrationError("invalid")))

    with pytest.raises(MigrationError, match="invalid"):
        migrate_to_v10(db_path, tmp_path / "backups")

    assert db_path.read_bytes() == before


def test_repository_enforces_three_active_top_tasks(tmp_path):
    db_path = tmp_path / "tasks.db"
    make_legacy_database(db_path)
    migrate_to_v10(db_path, tmp_path / "backups")
    repository = TaskRepository(db_path)
    for number in range(3):
        repository.save(TaskDraft(title=f"Top {number}", is_top_three=True))
    with pytest.raises(ValueError, match="Top 3"):
        repository.save(TaskDraft(title="Top 4", is_top_three=True))


def test_repository_round_trips_people_tags_and_v10_dates(tmp_path):
    from datetime import date

    db_path = tmp_path / "tasks.db"
    make_legacy_database(db_path)
    migrate_to_v10(db_path, tmp_path / "backups")
    repository = TaskRepository(db_path)

    task_id = repository.save(TaskDraft(
        title="Jour fixe vorbereiten",
        planning_date=date(2026, 9, 29),
        deadline=date(2026, 10, 2),
        people_tags=("Anna", "Einkauf"),
    ))

    stored = repository.get(task_id)
    assert stored is not None
    assert stored.draft.planning_date == date(2026, 9, 29)
    assert stored.draft.deadline == date(2026, 10, 2)
    assert stored.draft.people_tags == ("Anna", "Einkauf")


def test_weekly_goal_and_review_state_constraints_are_persisted(tmp_path):
    db_path = tmp_path / "tasks.db"
    make_legacy_database(db_path)
    migrate_to_v10(db_path, tmp_path / "backups")
    connection = sqlite3.connect(db_path)
    connection.execute("INSERT INTO weekly_goals(year,week,title,position) VALUES(2026,40,'Vertrieb klären',1)")
    connection.execute("INSERT INTO review_sessions(year,week,current_step,updated_at) VALUES(2026,40,3,'2026-09-26T20:00:00')")
    connection.commit()
    assert connection.execute("SELECT title FROM weekly_goals WHERE year=2026 AND week=40").fetchone()[0] == "Vertrieb klären"
    assert connection.execute("SELECT current_step FROM review_sessions WHERE year=2026 AND week=40").fetchone()[0] == 3
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO weekly_goals(year,week,title,position) VALUES(2026,40,'Ungültig',4)")
    connection.close()
