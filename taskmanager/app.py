import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton
from .db import init_db, DB_PATH, backup_db
from .ui import MainWindow, STYLE
from .priority_sync import apply_priority_sync
from .overview import install_overview_navigation
from .style_v63 import V63_STYLE, apply_v63_visuals
from .style_v64 import V64_STYLE, apply_v64_visuals
from .style_v7 import V7_STYLE
from .responsive_table_v7 import configure_responsive_task_area
from .editor_controls_v7 import configure_editor_subtask_controls
from .workspace_interactions_v7 import apply_workspace_interaction_fixes
from .style_v8 import V8_STYLE, rebuild_v8_shell, install_v8_responsive_behavior

VERSION = "8.0"


def _install_v8_secondary_actions(window):
    nav = getattr(window, "_v8_nav", None)
    if nav is None:
        return
    layout = nav.layout()
    if layout is None or getattr(window, "_v8_secondary_installed", False):
        return
    divider = QPushButton("Export / Hilfe")
    divider.setObjectName("v8Tool")
    divider.clicked.connect(window.export_excel)
    layout.addWidget(divider)
    settings = QPushButton("Einstellungen")
    settings.setObjectName("v8Tool")
    settings.clicked.connect(lambda: QMessageBox.information(window, "Einstellungen", "Lokale Datenbank · Offline-Betrieb · Excel-Export"))
    layout.addWidget(settings)
    window._v8_secondary_installed = True


def main():
    init_db()
    if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
        backup_db("startup")
    apply_priority_sync()
    a = QApplication(sys.argv)
    a.setStyle("Fusion")
    a.setStyleSheet(STYLE + V63_STYLE + V64_STYLE + V8_STYLE)
    w = MainWindow()
    install_overview_navigation(w)
    apply_v63_visuals(w)
    apply_v64_visuals(w)
    # Keep the legacy widget tree alive because refresh and existing functional
    # methods still depend on project/search/overview controls it owns.
    legacy_shell = w.centralWidget()
    rebuild_v8_shell(w)
    w._v8_legacy_shell = legacy_shell
    configure_responsive_task_area(w)
    configure_editor_subtask_controls(w)
    apply_workspace_interaction_fixes(w)
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
