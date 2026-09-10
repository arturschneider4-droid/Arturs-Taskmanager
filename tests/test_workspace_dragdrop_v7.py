from datetime import date, timedelta
import os


def _task(title="Planen"):
    return {
        "title": title,
        "description": "",
        "project_id": None,
        "priority": "important_not_urgent",
        "due_date": None,
        "status": "Offen",
        "recurrence": "none",
        "subtasks": [],
    }


def test_planning_drop_targets_get_dates_in_their_named_period(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from taskmanager import db
    from taskmanager.ui import MainWindow

    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        tid = db.save(_task(), make_backup=False)
        window.drop_moved(tid, "Später")
        later = db.task(tid)["due_date"]
        week_end = date.today() + timedelta(days=6 - date.today().weekday())
        assert date.fromisoformat(later) > week_end

        window.drop_moved(tid, "Diese Woche")
        this_week = db.task(tid)["due_date"]
        assert date.today() <= date.fromisoformat(this_week) <= week_end

        window.drop_moved(tid, "Heute")
        assert db.task(tid)["due_date"] == date.today().isoformat()
    finally:
        window.close()
