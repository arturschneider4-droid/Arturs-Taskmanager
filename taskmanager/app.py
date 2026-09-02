import sys
from PySide6.QtWidgets import QApplication
from .db import init_db, DB_PATH, backup_db
from .ui import MainWindow, STYLE
from .priority_sync import apply_priority_sync
from .overview import install_overview_navigation

VERSION = "6.2.2"


def main():
    init_db()
    if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
        backup_db("startup")
    apply_priority_sync()
    a = QApplication(sys.argv)
    a.setStyle("Fusion")
    a.setStyleSheet(STYLE)
    w = MainWindow()
    install_overview_navigation(w)
    w.setWindowTitle(f"Arturs Taskmanager V{VERSION}")
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    main()
