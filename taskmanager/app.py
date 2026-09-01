import sys
from PySide6.QtWidgets import QApplication
from .db import init_db, DB_PATH, backup_db
from .ui import MainWindow,STYLE
def main():
 init_db();
 if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
  backup_db("startup")
 a=QApplication(sys.argv);a.setStyle("Fusion");a.setStyleSheet(STYLE);w=MainWindow();w.show();sys.exit(a.exec())
if __name__=="__main__":main()
