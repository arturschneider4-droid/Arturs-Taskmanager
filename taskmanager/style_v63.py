"""Visual layer for V6.3.

Presentation-only changes. V6.2.2 application logic remains unchanged.
"""

from PySide6.QtWidgets import QAbstractItemView, QLabel, QTableWidget

V63_STYLE = r"""
/* ---------- V6.3: clean enterprise visual system ---------- */
QMainWindow, QWidget { background: #f5f7f9; color: #172b3a; }
#topbar { background: #ffffff; border-bottom: 1px solid #dce4e9; }
#brand { color: #172b3a; font-size: 18pt; font-weight: 700; }
#version { background: #f3f6f8; color: #566772; border: 1px solid #d7e0e5; border-radius: 7px; padding: 4px 9px; font-weight: 600; }
#sidebar { background: #034a70; border-right: 1px solid #0b5c82; }
QPushButton#nav { color: #eaf4f9; background: transparent; border: 0; border-radius: 8px; padding: 9px 13px; min-height: 40px; max-height: 42px; font-size: 10.5pt; font-weight: 600; text-align: left; }
QPushButton#nav:hover { background: #075c84; color: #ffffff; }
QPushButton#nav[active="true"] { background: #087cc1; color: #ffffff; }
#sideSearch { background: #063c57; color: #ffffff; border: 1px solid #38657b; border-radius: 8px; padding: 8px 10px; }
#sideSearch::placeholder { color: #bfd2dc; }
QListWidget#themes { background: transparent; border: 0; padding: 2px 0; }
QListWidget#themes::item { color: #eaf4f9; background: transparent; border-radius: 7px; padding: 7px 10px; margin: 1px 0; }
QListWidget#themes::item:hover { background: #075c84; }
QListWidget#themes::item:selected { background: #087cc1; color: #ffffff; font-weight: 700; }
#overview { background: #063f5d; border: 1px solid #2e647d; border-radius: 10px; padding: 4px; }
#overviewTitle { color: #d9e9f1; font-size: 8pt; font-weight: 700; letter-spacing: 1px; }
#overviewItem { color: #f4f9fb; background: transparent; border-radius: 6px; padding: 5px 6px; font-weight: 600; }
#overviewItem:hover { background: #075c84; }
#overviewCount { background: #087cc1; color: #ffffff; border-radius: 10px; padding: 2px 7px; min-width: 12px; font-weight: 700; }
QLineEdit, QComboBox, QDateEdit, QTextEdit { background: #ffffff; color: #172b3a; border: 1px solid #d3dee5; border-radius: 8px; padding: 8px 10px; selection-background-color: #0a82c8; }
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus { border: 1px solid #0074bd; background: #ffffff; }
QPushButton#primary { background: #0050a4; border: 0; border-radius: 8px; color: #ffffff; padding: 10px 17px; font-weight: 700; }
QPushButton#primary:hover { background: #0068c9; }
QPushButton#soft { background: #ffffff; border: 1px solid #d5dfe5; border-radius: 8px; color: #253744; padding: 9px 12px; }
QPushButton#soft:hover { background: #f0f5f8; border-color: #bfcfd8; }
QPushButton#tab { background: transparent; border: 0; color: #334957; padding: 10px 14px; font-weight: 600; }
QPushButton#tab:hover { color: #0050a4; }
QPushButton#tab[active="true"] { color: #0050a4; border-bottom: 2px solid #0050a4; }
QTableWidget { background: #ffffff; alternate-background-color: #fbfcfd; border: 1px solid #dce4e9; border-radius: 10px; gridline-color: #edf1f3; outline: none; }
QTableWidget::item { padding: 9px 9px; border-bottom: 1px solid #eef2f4; }
QTableWidget::item:hover { background: #f5f9fc; }
QTableWidget::item:selected { background: #eaf4fb; color: #172b3a; }
QHeaderView::section { background: #f8fafb; color: #607582; border: 0; border-bottom: 1px solid #dce4e9; padding: 10px 9px; font-weight: 700; }
.card { background: #ffffff; border: 1px solid #dce4e9; border-radius: 10px; }
.sectionLabel { color: #607582; font-size: 8.5pt; font-weight: 700; letter-spacing: .6px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QCheckBox::indicator:unchecked { background: #ffffff; border: 1px solid #b9c8d1; border-radius: 4px; }
QCheckBox::indicator:checked { background: #087cc1; border: 1px solid #087cc1; border-radius: 4px; }
QScrollBar:vertical { width: 9px; background: transparent; margin: 2px; }
QScrollBar::handle:vertical { background: #9bb2bf; border-radius: 4px; min-height: 28px; }
QScrollBar::handle:vertical:hover { background: #6f8f9f; }
QToolTip { background: #172b3a; color: #ffffff; border: 0; padding: 6px 8px; }
"""


def apply_v63_visuals(window):
    """Apply presentation-only adjustments after MainWindow has been built."""
    for label in window.findChildren(QLabel):
        if label.objectName() == "version" or label.text().strip() == "V6.2":
            label.setText("V6.3")
            label.setObjectName("version")

    table = window.findChild(QTableWidget)
    if table is not None:
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.verticalHeader().setDefaultSectionSize(58)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
