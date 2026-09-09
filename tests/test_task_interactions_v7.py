import os


def test_real_task_table_checkbox_changes_database_status(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from taskmanager import db
    from taskmanager.ui import MainWindow
    from taskmanager.responsive_table_v7 import configure_responsive_task_area

    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    tid = db.save({
        "title": "Checkbox Test",
        "description": "",
        "project_id": None,
        "priority": "important_not_urgent",
        "due_date": None,
        "status": "Offen",
        "recurrence": "none",
        "subtasks": [],
    }, make_backup=False)
    window.refresh_all()
    configure_responsive_task_area(window)
    app.processEvents()

    row = next(
        r for r in range(window.table.rowCount())
        if window.table.item(r, 1).data(Qt.UserRole) == tid
    )
    cell = window.table.cellWidget(row, 0)
    assert cell is not None
    cell.show()
    window.table.show()
    app.processEvents()

    QTest.mouseClick(cell, Qt.LeftButton, pos=cell.rect().center())
    app.processEvents()
    assert db.task(tid)["status"] == "Erledigt"

    QTest.mouseClick(cell, Qt.LeftButton, pos=cell.rect().center())
    app.processEvents()
    assert db.task(tid)["status"] == "Offen"

    window.close()
