import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "taskmanager" / "style_v7.py"


def test_v7_has_a_dedicated_themes_workspace():
    text = STYLE.read_text(encoding="utf-8")
    assert "def _build_themes_workspace(window):" in text
    assert "v7ThemesWorkspace" in text
    assert "refresh_themes_workspace" in text


def test_themes_navigation_is_a_real_stack_view():
    text = STYLE.read_text(encoding="utf-8")
    assert "themes_page = _build_themes_workspace(window)" in text
    assert "stack.addWidget(themes_page)" in text
    assert "stack.setCurrentWidget(themes_page)" in text
    assert 'window.title_label.setText("Themengebiete")' in text


def test_themes_workspace_exposes_create_edit_delete_actions():
    text = STYLE.read_text(encoding="utf-8")
    assert "window.new_project" in text
    assert "window.edit_project" in text
    assert "window.delete_project" in text


def test_themes_navigation_switches_to_the_dedicated_page():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from taskmanager.db import init_db
    from taskmanager.ui import MainWindow
    from taskmanager.style_v7 import rebuild_professional_shell

    app = QApplication.instance() or QApplication([])
    init_db()
    window = MainWindow()
    rebuild_professional_shell(window)
    window.set_view("themes")
    app.processEvents()

    current = window.stack.currentWidget()
    assert current.objectName() == "v7ThemesWorkspace"
    assert window.title_label.text() == "Themengebiete"

    window.close()
    app.processEvents()
