import os


def test_task_checkbox_click_changes_status():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from taskmanager.db import init_db, save, task
    from taskmanager.ui import MainWindow
    from taskmanager.style_v7 import rebuild_professional_shell
    from taskmanager.responsive_table_v7 import configure_responsive_task_area

    app = QApplication.instance() or QApplication([])
    init_db()
    tid = save({
        "title": "Checkbox-Test",
        "description": "",
        "project_id": None,
        "priority": "important_not_urgent",
        "due_date": None,
        "status": "Offen",
        "recurrence": "none",
        "subtasks": [],
    }, make_backup=False)

    window = MainWindow()
    rebuild_professional_shell(window)
    configure_responsive_task_area(window)
    window.selected_task = tid
    window.refresh_all()
    window.show()
    app.processEvents()

    row = next(i for i in range(window.table.rowCount()) if window.table.item(i, 1).data(Qt.UserRole) == tid)
    cell = window.table.cellWidget(row, 0)
    assert cell is not None

    QTest.mouseClick(cell, Qt.LeftButton)
    app.processEvents()

    assert task(tid)["status"] == "Erledigt"
    window.close()
    app.processEvents()
