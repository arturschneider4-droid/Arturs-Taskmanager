import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QHeaderView
from .db import init_db, DB_PATH, backup_db, latest_backup
from .ui import MainWindow, STYLE
from .priority_sync import apply_priority_sync
from .overview import install_overview_navigation
from .style_v63 import V63_STYLE, apply_v63_visuals
from .style_v64 import V64_STYLE, apply_v64_visuals
from .style_v7 import V7_STYLE, rebuild_professional_shell
from .responsive_table_v7 import configure_responsive_task_area
from .editor_controls_v7 import configure_editor_subtask_controls
from .workspace_interactions_v7 import apply_workspace_interaction_fixes
from .v8_interactions import install_drop_guard
from .style_v8 import V8_STYLE, rebuild_v8_shell, install_v8_responsive_behavior

VERSION = "8.0"
V7_COMPATIBILITY_VERSION = "7.1"

if not hasattr(QHeaderView, "Fixed"):
    QHeaderView.Fixed = QHeaderView.ResizeMode.Fixed


def _install_v8_secondary_actions(window):
    nav = getattr(window, "_v8_nav", None)
    if nav is None or getattr(window, "_v8_secondary_installed", False):
        return
    layout = nav.layout()
    if layout is None:
        return
    export = QPushButton("Export / Berichte")
    export.setObjectName("v8Tool")
    export.clicked.connect(window.export_excel)
    layout.addWidget(export)
    settings = QPushButton("Einstellungen")
    settings.setObjectName("v8Tool")
    settings.clicked.connect(lambda: QMessageBox.information(window, "Einstellungen", "Lokale Datenbank · Offline-Betrieb · Excel-Export"))
    layout.addWidget(settings)
    window._v8_secondary_installed = True


def _install_v7_secondary_actions(window):
    return _install_v8_secondary_actions(window)


def _sync_startup_undo_state(window):
    available = bool(latest_backup())
    window._undo_available = available
    window.undo_button.setEnabled(available)
    return available


def configure_main_window(window):
    install_overview_navigation(window)
    apply_v63_visuals(window)
    apply_v64_visuals(window)

    # Initialize the complete V7 shell first. V8 replaces its presentation
    # shell afterwards, but keeps the initialized functional widgets and
    # lifetime references so V7 startup utilities remain intact.
    legacy_shell = window.centralWidget()
    window._legacy_shell = legacy_shell
    rebuild_professional_shell(window)
    v7_shell = window.centralWidget()
    window._v7_legacy_shell = v7_shell
    if hasattr(window, "version_label"):
        window.version_label.setText(f"V{VERSION}")

    rebuild_v8_shell(window)
    window._v8_legacy_shell = v7_shell
    configure_responsive_task_area(window)
    configure_editor_subtask_controls(window)
    apply_workspace_interaction_fixes(window)
    install_drop_guard(window)
    _install_v7_secondary_actions(window)
    _install_v8_secondary_actions(window)
    install_v8_responsive_behavior(window)

    original_refresh_all = window.refresh_all

    def refresh_all_v8():
        original_refresh_all()
        from .style_v8 import _v8_refresh
        _v8_refresh(window)

    window.refresh_all = refresh_all_v8
    _sync_startup_undo_state(window)
    window.setMinimumSize(980, 700)
    window.setWindowTitle(f"Arturs Taskmanager V{VERSION}")
    return window


def main():
    init_db()
    if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
        backup_db("startup")
    apply_priority_sync()
    a = QApplication(sys.argv)
    a.setStyle("Fusion")
    a.setStyleSheet(STYLE + V63_STYLE + V64_STYLE + V7_STYLE + V8_STYLE)
    w = configure_main_window(MainWindow())
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
