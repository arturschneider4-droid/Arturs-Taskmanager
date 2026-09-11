import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton
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
from .style_v8 import V8_STYLE, rebuild_v8_shell, install_v8_responsive_behavior

VERSION = "8.0"
# Historical compatibility marker: the V7 release used VERSION = "7.1".
V7_COMPATIBILITY_VERSION = "7.1"


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
    """Compatibility wrapper retained while V8 owns the visible navigation."""
    return _install_v8_secondary_actions(window)


def main():
    init_db()
    if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
        backup_db("startup")
    apply_priority_sync()
    a = QApplication(sys.argv)
    a.setStyle("Fusion")
    a.setStyleSheet(STYLE + V63_STYLE + V64_STYLE + V7_STYLE + V8_STYLE)
    w = MainWindow()
    install_overview_navigation(w)
    apply_v63_visuals(w)
    apply_v64_visuals(w)
    legacy_shell = w.centralWidget()
    w._v7_legacy_shell = legacy_shell
    # Compatibility baseline: rebuild_professional_shell(w) remains imported,
    # while the approved V8 shell is the active presentation.
    rebuild_v8_shell(w)
    w._v8_legacy_shell = legacy_shell
    configure_responsive_task_area(w)
    configure_editor_subtask_controls(w)
    apply_workspace_interaction_fixes(w)
    _install_v7_secondary_actions(w)
    _install_v8_secondary_actions(w)
    install_v8_responsive_behavior(w)

    original_refresh_all = w.refresh_all

    def refresh_all_v8():
        original_refresh_all()
        from .style_v8 import _v8_refresh
        _v8_refresh(w)

    w.refresh_all = refresh_all_v8
    w.undo_button.setEnabled(False)
    w.setMinimumSize(980, 700)
    w.setWindowTitle(f"Arturs Taskmanager V{VERSION}")
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
