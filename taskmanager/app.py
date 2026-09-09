import sys
from PySide6.QtWidgets import QApplication
from .db import init_db, DB_PATH, backup_db
from .ui import MainWindow, STYLE
from .priority_sync import apply_priority_sync
from .overview import install_overview_navigation
from .style_v63 import V63_STYLE, apply_v63_visuals
from .style_v64 import V64_STYLE, apply_v64_visuals
from .style_v7 import V7_STYLE, rebuild_professional_shell
from .responsive_table_v7 import configure_responsive_task_area

VERSION = "7.1"


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
    # refresh logic still uses a few non-visible legacy controls (theme search
    # and overview counters) as data/UI dependencies.
    legacy_shell = w.centralWidget()
    rebuild_professional_shell(w)
    w._v7_legacy_shell = legacy_shell
    configure_responsive_task_area(w)
    # The task table and editor contain fixed-size interactive controls.
    # Below this width there is no honest layout in which every control can
    # remain visible, so the window stops before the UI starts overlapping.
    w.setMinimumSize(1260, 760)
    w.setWindowTitle(f"Arturs Taskmanager V{VERSION}")
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
