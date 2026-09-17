import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QToolButton

import taskmanager.db as db
import taskmanager.ui as ui
from taskmanager.style_v8 import rebuild_v8_shell


@pytest.fixture()
def v8_window(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "tasks.db"
    backup_dir = tmp_path / "backups"
    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(db, "BACKUP_DIR", backup_dir)
    monkeypatch.setattr(ui, "DB_PATH", db_path)
    db.init_db()

    c = db.connect()
    c.execute("INSERT INTO projects(name) VALUES (?)", ("V8 Testgebiet",))
    c.commit()
    c.close()

    app = QApplication.instance() or QApplication([])
    window = ui.MainWindow()
    rebuild_v8_shell(window)
    app.processEvents()
    window._v8_refresh_themes()
    app.processEvents()
    yield window
    window.close()
    window.deleteLater()
    app.processEvents()
    app.quit()


def test_v8_navigation_buttons_change_view(v8_window):
    window = v8_window
    buttons = {button.text().split("   ")[-1]: button for _, button in window._v8_nav_items}

    buttons["Kanban"].click()
    assert window.stack.currentWidget() is window.kanban

    buttons["Eisenhower"].click()
    assert window.stack.currentWidget() is window.eisen

    buttons["Planung"].click()
    assert window.stack.currentWidget() is window.plan

    buttons["Aufgaben"].click()
    assert window.stack.currentWidget() is window.tasks_page
    assert buttons["Aufgaben"].isChecked()


def test_v8_theme_selection_updates_project_and_returns_to_tasks(v8_window):
    window = v8_window
    assert window._v8_themes.count() == 1

    item = window._v8_themes.item(0)
    window._v8_themes.setCurrentItem(item)
    window._v8_themes.itemClicked.emit(item)
    QApplication.processEvents()

    assert window.project_filter == item.data(256)
    assert window.stack.currentWidget() is window.tasks_page


def test_v8_toolbar_and_responsive_controls_change_state(v8_window):
    window = v8_window
    buttons = window._v8_workspace.findChildren(QPushButton)
    detail = next(button for button in buttons if button.text() == "Detail")
    compact = next(button for button in buttons if button.text() == "Liste / Kompakt")
    sort = next(button for button in buttons if button.text() == "Sortieren")
    collapse = window._v8_nav.findChild(QToolButton)

    panel = window._v8_detail_panel
    assert panel.panel_open is True
    detail.click()
    assert panel.panel_open is False
    detail.click()
    assert panel.panel_open is True

    initial_height = window.table.verticalHeader().defaultSectionSize()
    compact.click()
    assert window.table.verticalHeader().defaultSectionSize() != initial_height

    initial_sort = window.sort_mode
    sort.click()
    assert window.sort_mode != initial_sort

    assert window._v8_nav.width() == 228
    collapse.click()
    assert window._v8_nav.width() == 60
