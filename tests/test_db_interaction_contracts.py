from datetime import date, timedelta
import sqlite3


def _task(title, due=None, status="Offen", priority="important_not_urgent"):
    return {
        "title": title,
        "description": "",
        "project_id": None,
        "priority": priority,
        "due_date": due,
        "status": status,
        "recurrence": "none",
        "subtasks": [],
    }


def test_due_filters_keep_later_and_unassigned_distinct(monkeypatch, tmp_path):
    from taskmanager import db

    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    today = date.today()
    week_end = today + timedelta(days=6 - today.weekday())
    no_due = db.save(_task("Ohne Datum"), make_backup=False)
    later = db.save(_task("Später", (week_end + timedelta(days=1)).isoformat()), make_backup=False)
    this_week = db.save(_task("Diese Woche", week_end.isoformat()), make_backup=False)

    assert {r["id"] for r in db.tasks(due="Ohne Fälligkeit")} == {no_due}
    assert {r["id"] for r in db.tasks(due="Später")} == {later}
    assert this_week not in {r["id"] for r in db.tasks(due="Später")}


def test_status_priority_and_due_updates_persist(monkeypatch, tmp_path):
    from taskmanager import db

    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    tid = db.save(_task("Persistenz"), make_backup=False)
    due = (date.today() + timedelta(days=5)).isoformat()
    db.update_status(tid, "Erledigt")
    db.update_priority(tid, "important_urgent")
    db.update_due(tid, due)

    row = db.task(tid)
    assert row["status"] == "Erledigt"
    assert row["priority"] == "important_urgent"
    assert row["due_date"] == due


def test_delete_cascades_subtasks(monkeypatch, tmp_path):
    from taskmanager import db

    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    tid = db.save(_task("Löschen"), make_backup=False)
    db.save({**_task("Löschen"), "subtasks": [("Unteraufgabe", False)]}, tid=tid, make_backup=False)
    assert len(db.subs(tid)) == 1

    db.remove(tid)
    assert db.task(tid) is None
    assert db.subs(tid) == []


def test_init_db_migrates_legacy_tasks_without_overwriting_user_data(monkeypatch, tmp_path):
    from taskmanager import db

    db_path = tmp_path / "tasks.db"
    connection = sqlite3.connect(db_path)
    connection.executescript(
        """
        CREATE TABLE projects(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);
        CREATE TABLE tasks(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          description TEXT NOT NULL DEFAULT '',
          project_id INTEGER,
          priority TEXT NOT NULL DEFAULT 'important_not_urgent',
          due_date TEXT,
          status TEXT NOT NULL DEFAULT 'Offen',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO tasks(title, description, priority, status)
        VALUES ('Bestehende Aufgabe', 'Bleibt erhalten', 'important_urgent', 'In Arbeit');
        """
    )
    connection.commit()
    connection.close()

    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    migrated = db.task(1)
    assert migrated["title"] == "Bestehende Aufgabe"
    assert migrated["description"] == "Bleibt erhalten"
    assert migrated["priority"] == "important_urgent"
    assert migrated["status"] == "In Arbeit"
    assert migrated["recurrence"] == "none"
    assert migrated["updated_at"]


def test_backup_restore_round_trip_recovers_previous_task_state(monkeypatch, tmp_path):
    from taskmanager import db

    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()
    task_id = db.save(_task("Vor Änderung"), make_backup=False)
    snapshot = db.backup_db("regression")

    db.save({**_task("Nach Änderung"), "description": "neu"}, task_id, make_backup=False)
    assert db.task(task_id)["title"] == "Nach Änderung"

    db.restore_backup(snapshot)
    assert db.task(task_id)["title"] == "Vor Änderung"
