import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QVBoxLayout
from .db import init_db, DB_PATH, backup_db
from .ui import MainWindow, STYLE
from .priority_sync import apply_priority_sync
from .overview import install_overview_navigation
from .style_v63 import V63_STYLE, apply_v63_visuals
from .style_v64 import V64_STYLE, apply_v64_visuals
from .style_v7 import V7_STYLE, rebuild_professional_shell
from .responsive_table_v7 import configure_responsive_task_area
from .editor_controls_v7 import configure_editor_subtask_controls
from .workspace_interactions_v7 import apply_workspace_interaction_fixes

VERSION = "7.1"


def _install_v7_secondary_actions(window):
    """Keep non-core utilities reachable in the compact V7 navigation."""
    sidebar = window.findChild(type(window.centralWidget()), "v7Sidebar")
    if sidebar is None or sidebar.layout() is None:
        return
    layout = sidebar.layout()
    divider = sidebar.findChild(type(sidebar), "v7Divider")
    if divider is None:
        return
    insert_at = layout.indexOf(divider) + 1
    actions = [
        ("▧   Berichte & Export", window.export_excel),
        ("⚙   Einstellungen", lambda: QMessageBox.information(window, "Einstellungen", "Lokale Datenbank · Offline-Betrieb · Excel-Export")),
        ("?   Hilfe & Info", lambda: QMessageBox.information(window, "Hilfe & Info", "Aufgabe auswählen, über die Ampel priorisieren und per Kanban oder Planung verschieben.")),
    ]
    for text, callback in actions:
        button = QPushButton(text)
        button.setObjectName("v7Nav")
        button.clicked.connect(callback)
        layout.insertWidget(insert_at, button)
        insert_at += 1


def main():
    init_db()
    if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
        backup_db("startup")
    apply_priority_sync()
    a = QApplication(sys.argv)
    a.setStyle("Fusion")
    a.setStyleSheet(STYLE + V63_STYLE + V64_STYLE + V7_STYLE)
    w = MainWindow()
    install_overview_navigation(w)
    apply_v63_visuals(w)
    apply_v64_visuals(w)
    # V7 replaces the legacy central widget. Keep that widget alive because
    # refresh logic still uses a few non-visible legacy controls as dependencies.
    legacy_shell = w.centralWidget()
    rebuild_professional_shell(w)
    w._v7_legacy_shell = legacy_shell
    configure_responsive_task_area(w)
    configure_editor_subtask_controls(w)
    apply_workspace_interaction_fixes(w)
    _install_v7_secondary_actions(w)

    # V7's themes page is generated from the live project list. Ensure every
    # project mutation immediately updates that page when it is visible.
    original_refresh_all = w.refresh_all

    def refresh_all_v7():
        original_refresh_all()
        page = w.findChild(type(w.centralWidget()), "v7ThemesWorkspace")
        if page is not None and hasattr(page, "refresh_themes_workspace") and page.isVisible():
            page.refresh_themes_workspace()

    w.refresh_all = refresh_all_v7

    version_label = w.findChild(type(w.centralWidget()), "v7Version")
    if version_label is not None:
        version_label.setText(f"V{VERSION}")

    # A startup backup is not an undoable user action. Undo becomes enabled
    # only after an actual change creates a current backup.
    w.undo_button.setEnabled(False)

    # The task table and editor contain fixed-size interactive controls.
    # Below this width there is no honest layout in which every control can
    # remain visible, so the window stops before the UI starts overlapping.
    w.setMinimumSize(1260, 760)
    w.setWindowTitle(f"Arturs Taskmanager V{VERSION}")
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
