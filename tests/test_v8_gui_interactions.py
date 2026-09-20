import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QToolButton

import taskmanager.db as db
import taskmanager.ui as ui
import taskmanager.style_v8 as style_v8
from taskmanager.app import _install_v8_secondary_actions
from taskmanager.style_v8 import rebuild_v8_shell


@pytest.fixture()
def v8_window(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "tasks.db"
    backup_dir = tmp_path / "backups"
    monkeypatch.setattr(db, "APP_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(db, "BACKUP_DIR", backup_dir)
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

    assert window.project_filter == item.data(Qt.UserRole)
    assert window.stack.currentWidget() is window.tasks_page
    chips = window._v8_filter_chips.findChildren(QPushButton, "v8Chip")
    assert any(chip.property("filterKey") == "theme" for chip in chips)


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

    assert hasattr(style_v8, "_create_sort_menu")
    menu = style_v8._create_sort_menu(window, sort)
    title_action = next(action for action in menu.actions() if action.text() == "Titel")
    title_action.trigger()
    assert window.sort_mode == 2

    assert window._v8_nav.width() == 228
    collapse.click()
    assert window._v8_nav.width() == 60


def test_collapsed_navigation_hides_secondary_labels_and_footer(v8_window):
    window = v8_window
    _install_v8_secondary_actions(window)
    collapse = window._v8_nav.findChild(QToolButton)
    secondary = [
        button
        for button in window._v8_nav.findChildren(QPushButton)
        if button.text() in {"Export / Berichte", "Einstellungen"}
    ]
    assert len(secondary) == 2

    collapse.click()
    QApplication.processEvents()

    assert all(button.isHidden() for button in secondary)
    assert window._v8_nav.findChild(QLabel, "v8NavFooter").isHidden()
    assert all(
        label.isHidden()
        for label in window._v8_nav.findChildren(QLabel, "v8NavHeader")
    )


def test_task_badges_are_not_clipped_with_open_detail_panel(v8_window):
    window = v8_window
    connection = db.connect()
    project_id = connection.execute(
        "INSERT INTO projects(name) VALUES (?)", ("Vertrieb & Kunden",)
    ).lastrowid
    connection.commit()
    connection.close()
    db.save(
        {
            "title": "Ausführlicher Aufgabentitel",
            "description": "",
            "project_id": project_id,
            "priority": "important_not_urgent",
            "due_date": None,
            "status": "In Arbeit",
            "recurrence": "none",
            "subtasks": [],
        },
        make_backup=False,
    )
    window.setStyleSheet(style_v8.V8_STYLE)
    window.resize(1440, 900)
    window.show()
    window.refresh_all()
    QApplication.processEvents()

    theme = window.table.cellWidget(0, 2)
    status = window.table.cellWidget(0, 5)
    assert theme.text() == "Vertrieb & Kunden"
    assert theme.width() >= theme.minimumSizeHint().width()
    assert status.text() == "In Arbeit"
    assert status.width() >= status.minimumSizeHint().width()


def test_v8_detail_toggle_tracks_requested_state_while_responsive_layout_hides_panel(v8_window):
    window = v8_window
    detail = next(
        button
        for button in window._v8_workspace.findChildren(QPushButton)
        if button.text() == "Detail"
    )
    panel = window._v8_detail_panel

    panel.handle_window_width(panel.NARROW_BREAKPOINT - 1)
    assert window.editor.isVisible() is False
    assert panel.panel_open is True

    detail.click()
    assert panel.panel_open is False

    detail.click()
    assert panel.panel_open is True


def test_active_filter_is_visible_as_removable_chip(v8_window):
    window = v8_window
    window.pfilter.setCurrentIndex(1)
    QApplication.processEvents()

    chips = window._v8_filter_chips.findChildren(QPushButton, "v8Chip")
    priority_chip = next(chip for chip in chips if chip.property("filterKey") == "priority")
    assert "Priorität:" in priority_chip.text()

    priority_chip.click()
    QApplication.processEvents()
    assert window.pfilter.currentIndex() == 0


def test_grouping_state_is_visible_and_can_be_cleared(v8_window):
    window = v8_window
    style_v8._set_group(window, "Themengebiet")
    QApplication.processEvents()

    chips = window._v8_filter_chips.findChildren(QPushButton, "v8Chip")
    group_chip = next(chip for chip in chips if chip.property("filterKey") == "group")
    assert group_chip.text() == "Gruppiert: Themengebiet  ×"

    group_chip.click()
    QApplication.processEvents()
    assert window._v8_group == "Keine Gruppierung"


def test_grouping_reorders_widget_backed_theme_column(v8_window):
    window = v8_window
    connection = db.connect()
    first_project = connection.execute(
        "SELECT id FROM projects WHERE name=?", ("V8 Testgebiet",)
    ).fetchone()["id"]
    second_project = connection.execute(
        "INSERT INTO projects(name) VALUES (?)", ("Anderes Gebiet",)
    ).lastrowid
    connection.commit()
    connection.close()

    def task_data(title, project_id):
        return {
            "title": title,
            "description": "",
            "project_id": project_id,
            "priority": "important_not_urgent",
            "due_date": None,
            "status": "Offen",
            "recurrence": "none",
            "subtasks": [],
        }

    db.save(task_data("Zweiter", first_project), make_backup=False)
    db.save(task_data("Erster", second_project), make_backup=False)
    db.save(task_data("Dritter", first_project), make_backup=False)
    window.refresh_all()

    style_v8._set_group(window, "Themengebiet")
    QApplication.processEvents()
    themes = [window.table.cellWidget(row, 2).text() for row in range(window.table.rowCount())]
    assert themes == sorted(themes, key=str.casefold)


def test_removing_scope_due_chip_resets_scope_state(v8_window):
    window = v8_window
    window.set_scope("Heute")
    QApplication.processEvents()
    due_chip = next(
        chip
        for chip in window._v8_filter_chips.findChildren(QPushButton, "v8Chip")
        if chip.property("filterKey") == "due"
    )

    due_chip.click()
    QApplication.processEvents()

    assert window.scope == "Alle"
    all_scope = next(button for key, button in window._v8_scopes if key == "Alle")
    assert all_scope.property("active") == "true"


def test_completed_scope_filters_completed_tasks(v8_window):
    window = v8_window
    completed_id = db.save(
        {
            "title": "Erledigte Aufgabe",
            "description": "",
            "project_id": None,
            "priority": "important_not_urgent",
            "due_date": None,
            "status": "Erledigt",
            "recurrence": "none",
            "subtasks": [],
        },
        make_backup=False,
    )
    db.save(
        {
            "title": "Offene Aufgabe",
            "description": "",
            "project_id": None,
            "priority": "important_not_urgent",
            "due_date": None,
            "status": "Offen",
            "recurrence": "none",
            "subtasks": [],
        },
        make_backup=False,
    )

    window.set_scope("Erledigt")
    QApplication.processEvents()

    visible_ids = [
        window.table.item(row, 1).data(Qt.UserRole)
        for row in range(window.table.rowCount())
    ]
    assert visible_ids == [completed_id]
    assert window.sfilter.currentText() == "Erledigt"

    window.set_scope("Alle")
    QApplication.processEvents()

    visible_ids = {
        window.table.item(row, 1).data(Qt.UserRole)
        for row in range(window.table.rowCount())
    }
    assert visible_ids == {completed_id, completed_id + 1}
    assert window.sfilter.currentText() == "Alle Status"


@pytest.mark.parametrize("view_key,lane_attribute", [
    ("kanban", "kcols"),
    ("eisenhower", "ecols"),
    ("planning", "pcols"),
])
def test_board_selection_opens_and_synchronizes_detail_panel(
    v8_window, view_key, lane_attribute
):
    window = v8_window
    task_id = db.save(
        {
            "title": "Auswahltest",
            "description": "",
            "project_id": None,
            "priority": "important_urgent",
            "due_date": None,
            "status": "Offen",
            "recurrence": "none",
            "subtasks": [],
        },
        make_backup=False,
    )
    window.refresh_all()
    window.set_view(view_key)
    panel = window._v8_detail_panel
    panel.set_panel_open(False)
    lanes = getattr(window, lane_attribute)
    lane = next(widget for widget in lanes.values() if widget.count())
    item = lane.item(0)

    lane.setCurrentItem(item)
    lane.itemClicked.emit(item)
    QApplication.processEvents()

    assert item.data(Qt.UserRole) == task_id
    assert window.selected_task == task_id
    assert window.editor_task_id == task_id
    assert panel.task_id == task_id
    assert panel.panel_open is True
