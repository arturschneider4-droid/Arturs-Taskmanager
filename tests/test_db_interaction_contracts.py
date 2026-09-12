from datetime import date, timedelta


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
