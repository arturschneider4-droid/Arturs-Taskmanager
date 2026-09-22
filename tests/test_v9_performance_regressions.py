import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

import taskmanager.db as db
import taskmanager.ui as ui
from taskmanager.app import configure_main_window
from taskmanager.ui import MainWindow


def test_task_refresh_loads_subtask_summaries_without_per_row_connections(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    connection = db.connect()
    for number in range(20):
        task_id = connection.execute(
            "INSERT INTO tasks(title, priority, status, recurrence) VALUES(?,?,?,?)",
            (f"Aufgabe {number}", "important_not_urgent", "Offen", "none"),
        ).lastrowid
        connection.execute(
            "INSERT INTO subtasks(task_id, title, done) VALUES(?,?,?)",
            (task_id, "Erledigt", 1),
        )
        connection.execute(
            "INSERT INTO subtasks(task_id, title, done) VALUES(?,?,?)",
            (task_id, "Offen", 0),
        )
    connection.commit()
    connection.close()

    app = QApplication.instance() or QApplication([])
    window = configure_main_window(MainWindow())
    app.processEvents()

    real_connect = db.connect
    connection_count = 0

    def counted_connect():
        nonlocal connection_count
        connection_count += 1
        return real_connect()

    monkeypatch.setattr(db, "connect", counted_connect)
    window.refresh_tasks()

    assert window.table.rowCount() == 20
    assert "Unteraufgaben: 1 / 2" in window.table.item(0, 1).text()
    assert connection_count <= 2
    window.close()


def test_scope_switch_refreshes_the_interface_only_once(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    app = QApplication.instance() or QApplication([])
    window = configure_main_window(MainWindow())
    window.set_scope("Heute")
    app.processEvents()

    real_connect = db.connect
    connection_count = 0

    def counted_connect():
        nonlocal connection_count
        connection_count += 1
        return real_connect()

    monkeypatch.setattr(db, "connect", counted_connect)
    monkeypatch.setattr(ui, "connect", counted_connect)
    window.set_scope("Erledigt")
    app.processEvents()

    assert window.scope == "Erledigt"
    assert window.sfilter.currentText() == "Erledigt"
    assert window.dfilter.currentText() == "Alle Fälligkeiten"
    assert connection_count <= 6
    window.close()
