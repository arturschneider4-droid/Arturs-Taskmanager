import gc
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

import taskmanager.db as db
from taskmanager.editor_controls_v7 import configure_editor_subtask_controls
from taskmanager.responsive_table_v7 import configure_responsive_task_area
from taskmanager.style_v7 import rebuild_professional_shell
from taskmanager.style_v8 import rebuild_v8_shell, install_v8_responsive_behavior
from taskmanager.ui import MainWindow
from taskmanager.v8_interactions import install_drop_guard
from taskmanager.workspace_interactions_v7 import apply_workspace_interaction_fixes


def _task(title, *, project_id=None, due_date=None):
    return {
        "title": title,
        "description": f"Beschreibung für {title}",
        "project_id": project_id,
        "priority": "important_not_urgent",
        "due_date": due_date,
        "status": "Offen",
        "recurrence": "none",
        "subtasks": [("Prüfschritt", False)],
    }


def _build_production_window():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    legacy_shell = window.centralWidget()
    rebuild_professional_shell(window)
    window._v7_legacy_shell = legacy_shell
    gc.collect()
    app.processEvents()
    rebuild_v8_shell(window)
    window._v8_legacy_shell = legacy_shell
    configure_responsive_task_area(window)
    configure_editor_subtask_controls(window)
    apply_workspace_interaction_fixes(window)
    install_drop_guard(window)
    install_v8_responsive_behavior(window)
    window.setMinimumSize(980, 700)
    window.show()
    app.processEvents()
    return app, window


def test_production_shell_supports_core_flow_and_restart(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    connection = db.connect()
    project_id = connection.execute(
        "INSERT INTO projects(name) VALUES (?)", ("Releaseprüfung",)
    ).lastrowid
    connection.commit()
    connection.close()
    task_id = db.save(_task("V8 Ablauf", project_id=project_id), make_backup=False)

    app, window = _build_production_window()
    try:
        panel = window._v8_detail_panel
        assert panel.panel_open is True
        assert window.editor.isVisible() is True

        window.select_task(task_id)
        window.set_project(project_id)
        assert window.table.rowCount() == 1

        window.search.setText("Ablauf")
        app.processEvents()
        assert window.table.rowCount() == 1
        window.search.setText("nicht vorhanden")
        app.processEvents()
        assert window.table.rowCount() == 0
        window.search.clear()

        window.cycle_priority(task_id)
        window.drop_moved(task_id, "Erledigt")
        assert db.task(task_id)["status"] == "Erledigt"
        assert db.task(task_id)["priority"] != "important_not_urgent"

        for view, widget in (
            ("kanban", window.kanban),
            ("eisenhower", window.eisen),
            ("planning", window.plan),
            ("tasks", window.tasks_page),
        ):
            window.set_view(view)
            assert window.stack.currentWidget() is widget
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()

    app, restarted = _build_production_window()
    try:
        persisted = db.task(task_id)
        assert persisted is not None
        assert persisted["status"] == "Erledigt"
        assert restarted._v8_detail_panel.panel_open is True
    finally:
        restarted.close()
        restarted.deleteLater()
        app.processEvents()


def test_v8_minimum_window_hides_detail_and_collapses_navigation(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "tasks.db")
    monkeypatch.setattr(db, "BACKUP_DIR", tmp_path / "backups")
    db.init_db()

    app, window = _build_production_window()
    try:
        window.resize(980, 700)
        app.processEvents()

        assert window.width() == 980
        assert window.editor.isVisible() is False
        assert window._v8_detail_panel.panel_open is True
        assert window._v8_nav.width() == 60
        assert window.table.width() >= 800
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()
