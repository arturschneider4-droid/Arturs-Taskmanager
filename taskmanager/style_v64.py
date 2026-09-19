"""V6.4 premium enterprise visual system.

Presentation-first layer for the existing PySide6 application. It deliberately
keeps the database and task logic untouched while providing a cohesive visual
language and a dedicated Themes workspace adapter.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QVBoxLayout, QWidget
)

V64_STYLE = r"""
/* ================================================================
   ARTURS TASKMANAGER V6.4 — PREMIUM ENTERPRISE DESIGN SYSTEM
   ================================================================ */

* {
    font-family: "Segoe UI";
    font-size: 10pt;
    color: #183247;
}
QMainWindow, QWidget { background: #F4F7FA; }

/* --- shell ----------------------------------------------------- */
#topbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E1E8EE;
}
#brand {
    color: #163A55;
    font-size: 20pt;
    font-weight: 700;
}
#version {
    background: #F1F5F8;
    color: #667784;
    border: 1px solid #DCE5EB;
    border-radius: 8px;
    padding: 4px 9px;
    font-size: 9pt;
    font-weight: 600;
}

/* --- sidebar --------------------------------------------------- */
#sidebar {
    background: #083E5A;
    border-right: 1px solid #0D536F;
}
#sideTitle, #overviewTitle {
    color: #AFC8D6;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1.1px;
}
#sideSearch {
    background: #07354C;
    color: #F6FBFD;
    border: 1px solid #2A6179;
    border-radius: 8px;
    padding: 9px 11px;
}
#sideSearch:focus { border: 1px solid #49A9D8; }
#sideSearch::placeholder { color: #8FAFBE; }
QPushButton#nav {
    color: #E3EFF5;
    background: transparent;
    border: 0;
    border-radius: 8px;
    text-align: left;
    padding: 9px 13px;
    min-height: 40px;
    max-height: 42px;
    font-size: 10.5pt;
    font-weight: 600;
}
QPushButton#nav:hover { background: #0D506E; color: #FFFFFF; }
QPushButton#nav[active="true"] {
    background: #0B78B5;
    color: #FFFFFF;
}
QPushButton#nav[active="true"]:hover { background: #1187C5; }
QPushButton#sideAction {
    background: #0A5878;
    color: #FFFFFF;
    border: 1px solid #34758E;
    border-radius: 8px;
    padding: 9px 12px;
    font-weight: 600;
    min-height: 40px;
}
QPushButton#sideAction:hover { background: #0C698E; }
QListWidget#themes {
    background: transparent;
    border: 0;
    outline: none;
    padding: 2px 0;
}
QListWidget#themes::item {
    color: #DDECF3;
    background: transparent;
    border-radius: 7px;
    padding: 8px 10px;
    margin: 1px 0;
    min-height: 22px;
}
QListWidget#themes::item:hover { background: #0D506E; color: #FFFFFF; }
QListWidget#themes::item:selected {
    background: #0B78B5;
    color: #FFFFFF;
    font-weight: 700;
}
#overview {
    background: #073A54;
    border: 1px solid #2A6179;
    border-radius: 10px;
    padding: 4px;
}
#overviewItem {
    color: #E8F2F7;
    background: transparent;
    border-radius: 6px;
    padding: 5px 6px;
    font-weight: 600;
}
#overviewItem:hover { background: #0D506E; }
#overviewCount {
    background: #0B78B5;
    color: #FFFFFF;
    border-radius: 10px;
    padding: 2px 7px;
    min-width: 12px;
    font-weight: 700;
}

/* --- typography / workspace ---------------------------------- */
QLabel#pageTitle { color: #163A55; font-size: 22pt; font-weight: 700; }
QLabel#pageSubtitle { color: #71818C; font-size: 10pt; }
.sectionLabel {
    color: #71818C;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1px;
}

/* --- controls -------------------------------------------------- */
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background: #FFFFFF;
    color: #183247;
    border: 1px solid #D5E0E7;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #0B78B5;
}
QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QTextEdit:hover { border-color: #B9CAD5; }
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 1px solid #1689C5;
    background: #FFFFFF;
}
QComboBox::drop-down { border: 0; width: 28px; }
QPushButton#primary {
    background: #0050A4;
    color: #FFFFFF;
    border: 0;
    border-radius: 8px;
    padding: 10px 17px;
    font-weight: 700;
}
QPushButton#primary:hover { background: #0069C8; }
QPushButton#primary:pressed { background: #00478F; }
QPushButton#soft {
    background: #FFFFFF;
    color: #294353;
    border: 1px solid #D5E0E7;
    border-radius: 8px;
    padding: 9px 12px;
}
QPushButton#soft:hover { background: #F1F6F9; border-color: #BFCFD9; }

/* --- segmented scope tabs ------------------------------------ */
QPushButton#tab {
    background: transparent;
    color: #5D7180;
    border: 0;
    border-radius: 7px;
    padding: 8px 13px;
    font-weight: 600;
}
QPushButton#tab:hover { background: #EAF2F7; color: #0050A4; }
QPushButton#tab[active="true"] {
    background: #E6F1F8;
    color: #0050A4;
    font-weight: 700;
}

/* --- surfaces -------------------------------------------------- */
.card {
    background: #FFFFFF;
    border: 1px solid #DEE7ED;
    border-radius: 12px;
}
QTableWidget {
    background: #FFFFFF;
    alternate-background-color: #FBFCFD;
    border: 0;
    gridline-color: transparent;
    outline: none;
}
QTableWidget::item {
    padding: 10px 10px;
    border-bottom: 1px solid #EEF2F5;
}
QTableWidget::item:hover { background: #F6FAFC; }
QTableWidget::item:selected { background: #EAF4FA; color: #173A52; }
QHeaderView::section {
    background: #F8FAFB;
    color: #6B7C88;
    border: 0;
    border-bottom: 1px solid #DDE6EC;
    padding: 10px 10px;
    font-size: 8.5pt;
    font-weight: 700;
}

/* --- lists / boards ------------------------------------------- */
QListWidget {
    background: #FBFCFD;
    border: 1px solid #E0E8ED;
    border-radius: 9px;
    outline: none;
    padding: 5px;
}
QListWidget::item {
    background: #FFFFFF;
    border: 1px solid #E6EDF1;
    border-radius: 8px;
    padding: 9px 10px;
    margin: 3px 1px;
}
QListWidget::item:hover { background: #F5FAFC; border-color: #C8DDE8; }
QListWidget::item:selected { background: #EAF4FA; color: #163A55; border-color: #9DC9DE; }

/* --- badges / semantic states -------------------------------- */
StatusBadge, ThemeBadge {
    border-radius: 8px;
    padding: 5px 10px;
    font-weight: 600;
}
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 17px; height: 17px; }
QCheckBox::indicator:unchecked { background: #FFFFFF; border: 1px solid #B8C9D3; border-radius: 5px; }
QCheckBox::indicator:checked { background: #0B78B5; border: 1px solid #0B78B5; border-radius: 5px; }

/* --- priority editor ------------------------------------------ */
PriorityCard {
    min-height: 88px;
    border-radius: 10px;
}

/* --- menus / scrollbars --------------------------------------- */
QMenu {
    background: #FFFFFF;
    border: 1px solid #DCE5EA;
    border-radius: 9px;
    padding: 5px;
}
QMenu::item { padding: 8px 24px 8px 10px; border-radius: 6px; }
QMenu::item:selected { background: #EAF4FA; color: #0050A4; }
QScrollBar:vertical { width: 9px; background: transparent; margin: 2px; }
QScrollBar::handle:vertical { background: #A6BBC7; border-radius: 4px; min-height: 28px; }
QScrollBar::handle:vertical:hover { background: #7895A5; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QToolTip { background: #163A55; color: #FFFFFF; border: 0; padding: 6px 8px; }

/* --- dedicated themes page ----------------------------------- */
#themesPageTitle { color: #163A55; font-size: 20pt; font-weight: 700; }
#themesPageSubtitle { color: #71818C; }
#themeTile {
    background: #FFFFFF;
    border: 1px solid #DEE7ED;
    border-radius: 12px;
}
#themeTile:hover { border-color: #A9CBDC; background: #FCFEFF; }
#themeTileName { color: #163A55; font-size: 12pt; font-weight: 700; }
#themeTileMeta { color: #71818C; font-size: 9pt; }
"""


def _theme_count(window, project_id):
    from .db import connect
    c = connect()
    try:
        return c.execute("SELECT COUNT(*) FROM tasks WHERE project_id=?", (project_id,)).fetchone()[0]
    finally:
        c.close()


def _build_themes_page(window):
    page = QWidget()
    page.setObjectName("themesPage")
    root = QVBoxLayout(page)
    root.setContentsMargins(2, 2, 2, 2)
    root.setSpacing(16)

    head = QHBoxLayout()
    titles = QVBoxLayout()
    title = QLabel("Themengebiete")
    title.setObjectName("themesPageTitle")
    subtitle = QLabel("Arbeitsbereiche verwalten und Aufgaben gezielt bündeln")
    subtitle.setObjectName("themesPageSubtitle")
    titles.addWidget(title)
    titles.addWidget(subtitle)
    head.addLayout(titles)
    head.addStretch()
    add = QPushButton("＋  Neues Themengebiet")
    add.setObjectName("primary")
    add.clicked.connect(window.new_project)
    head.addWidget(add)
    root.addLayout(head)

    tiles = QWidget()
    grid = QGridLayout(tiles)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(12)
    page._theme_grid = grid
    page._theme_tiles = []
    root.addWidget(tiles, 1)

    def refresh():
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        page._theme_tiles.clear()
        c = window.__class__
        from .db import connect
        db = connect()
        try:
            rows = db.execute("SELECT id,name FROM projects ORDER BY name").fetchall()
        finally:
            db.close()
        if not rows:
            empty = QLabel("Noch keine Themengebiete vorhanden.\nLege dein erstes Themengebiet an, um Aufgaben zu strukturieren.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setObjectName("themeTileMeta")
            grid.addWidget(empty, 0, 0, 1, 2)
            return
        for i, row in enumerate(rows):
            tile = QFrame()
            tile.setObjectName("themeTile")
            tile.setMinimumHeight(112)
            lay = QVBoxLayout(tile)
            lay.setContentsMargins(16, 14, 16, 12)
            name = QLabel(row["name"])
            name.setObjectName("themeTileName")
            meta = QLabel(f"{_theme_count(window, row['id'])} Aufgaben")
            meta.setObjectName("themeTileMeta")
            lay.addWidget(name)
            lay.addWidget(meta)
            lay.addStretch()
            actions = QHBoxLayout()
            open_b = QPushButton("Öffnen")
            open_b.setObjectName("soft")
            open_b.clicked.connect(lambda _, pid=row["id"]: (window.set_project(pid), window.set_view("tasks")))
            edit_b = QPushButton("Bearbeiten")
            edit_b.setObjectName("soft")
            edit_b.clicked.connect(lambda _, pid=row["id"]: window.edit_project(pid))
            delete_b = QPushButton("Löschen")
            delete_b.setObjectName("soft")
            delete_b.clicked.connect(lambda _, pid=row["id"]: window.delete_project(pid))
            actions.addWidget(open_b)
            actions.addWidget(edit_b)
            actions.addWidget(delete_b)
            lay.addLayout(actions)
            grid.addWidget(tile, i // 2, i % 2)
            page._theme_tiles.append(tile)

    page.refresh_themes = refresh
    refresh()
    return page


def _install_theme_navigation(window):
    original_set_view = window.set_view
    page = _build_themes_page(window)
    window.stack.addWidget(page)
    themes_index = window.stack.indexOf(page)

    def set_view(key):
        if key == "themes":
            window.stack.setCurrentIndex(themes_index)
            window.title_label.setText("Themengebiete")
            for k, b in window.nav:
                active = (k == "themes")
                b.setProperty("active", str(active).lower())
                b.setChecked(active)
                b.style().unpolish(b); b.style().polish(b); b.update()
            page.refresh_themes()
            return
        original_set_view(key)

    window.set_view = set_view
    for button in [b for _, b in window.nav] + [w for w in window.findChildren(QPushButton) if w.objectName() == "nav"]:
        if button.text().strip().endswith("Themengebiete") or "Themengebiete" in button.text():
            button.clicked.connect(lambda: window.set_view("themes"))


def apply_v64_visuals(window):
    """Apply V6.4 presentation adjustments and the functional Themes workspace."""
    for label in window.findChildren(QLabel):
        if label.objectName() == "version" or label.text().strip() in {"V6.2", "V6.3"}:
            label.setText("V6.4")
            label.setObjectName("version")

    title = getattr(window, "title_label", None)
    if title is not None:
        title.setObjectName("pageTitle")

    # Protect the proportions that caused the previous clipping issues.
    table = window.findChild(__import__("PySide6.QtWidgets", fromlist=["QTableWidget"]).QTableWidget)
    if table is not None:
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.verticalHeader().setDefaultSectionSize(60)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

    for card in window.findChildren(QWidget):
        if card.__class__.__name__ == "PriorityCard":
            card.setMinimumHeight(88)

    _install_theme_navigation(window)
