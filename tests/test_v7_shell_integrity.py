import gc
import os
from pathlib import Path


APP = Path(__file__).resolve().parents[1] / "taskmanager" / "app.py"


def _build_v7_window():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from taskmanager.db import init_db
    from taskmanager.ui import MainWindow
    from taskmanager.style_v7 import rebuild_professional_shell

    app = QApplication.instance() or QApplication([])
    init_db()
    window = MainWindow()
    legacy_shell = window.centralWidget()
    rebuild_professional_shell(window)
    # Mirror the production startup lifetime guard in app.main().
    window._v7_legacy_shell = legacy_shell
    gc.collect()
    app.processEvents()
    return app, window


def test_v7_shell_keeps_legacy_refresh_dependencies_alive():
    app, window = _build_v7_window()
    window.refresh_all()
    assert window.projects is not None
    assert window.stack is not None
    window.close()


def test_v7_startup_preserves_legacy_shell_lifetime_and_utilities():
    text = APP.read_text(encoding="utf-8")
    assert "legacy_shell = w.centralWidget()" in text
    assert "w._v7_legacy_shell = legacy_shell" in text
    assert "_install_v7_secondary_actions(w)" in text
    assert "window.export_excel" in text
    assert 'version_label.setText(f"V{VERSION}")' in text


def test_v7_themes_navigation_and_task_navigation_share_one_stack():
    app, window = _build_v7_window()

    window.set_view("themes")
    assert window.stack.currentWidget().objectName() == "v7ThemesWorkspace"
    window.set_view("tasks")
    assert window.stack.currentWidget() is window.tasks_page
    window.set_view("kanban")
    assert window.stack.currentWidget() is window.kanban
    window.set_view("eisenhower")
    assert window.stack.currentWidget() is window.eisen
    window.set_view("planning")
    assert window.stack.currentWidget() is window.plan
    window.close()
