"""V6.5 premium workspace shell.

This module rebuilds the application shell around the existing functional
widgets. Database and task-management behavior stays in ui.py/db.py.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QPushButton, QScrollArea,
    QVBoxLayout, QWidget
)

V65_STYLE = r"""
* { font-family: "Segoe UI"; font-size: 10pt; color: #173247; }
QMainWindow, QWidget { background: #F5F7F9; }

/* ===== application shell ===== */
#v65Topbar {
    background: #FFFFFF;
    border-bottom: 1px solid #DDE5EA;
}
#v65Brand { color: #123A55; font-size: 19pt; font-weight: 700; }
#v65Version {
    background: #EEF3F6; color: #60737F; border: 1px solid #D9E2E8;
    border-radius: 8px; padding: 4px 9px; font-size: 8.5pt; font-weight: 700;
}
#v65Offline {
    color: #617680; background: #F4F7F8; border: 1px solid #DCE5E9;
    border-radius: 8px; padding: 5px 9px; font-size: 8.5pt; font-weight: 600;
}
#v65TopSearch {
    background: #F7F9FA; border: 1px solid #D9E3E8; border-radius: 9px;
    padding: 9px 12px; color: #173247;
}
#v65TopSearch:focus { background: #FFFFFF; border-color: #5AA7CB; }

/* ===== navigation rail ===== */
#v65Sidebar {
    background: #083E5A; border-right: 1px solid #0D536F;
}
#v65SectionLabel {
    color: #93B3C3; font-size: 8pt; font-weight: 700; letter-spacing: 1px;
    padding: 2px 8px;
}
QPushButton#v65Nav {
    background: transparent; border: 0; border-radius: 9px; color: #DDECF3;
    text-align: left; padding: 9px 11px; min-height: 38px; max-height: 40px;
    font-size: 10pt; font-weight: 600;
}
QPushButton#v65Nav:hover { background: #0D506E; color: #FFFFFF; }
QPushButton#v65Nav[active="true"] { background: #0B78B5; color: #FFFFFF; }
QPushButton#v65Nav[active="true"]:hover { background: #1288C5; }
QPushButton#v65Secondary {
    background: transparent; border: 0; color: #AFC8D5; text-align: left;
    border-radius: 8px; padding: 8px 11px; min-height: 34px; max-height: 36px;
}
QPushButton#v65Secondary:hover { background: #0D506E; color: #FFFFFF; }
QFrame#v65Divider { background: #215B73; min-height: 1px; max-height: 1px; }

/* ===== themes area ===== */
#v65ThemePanel { background: #07374F; border: 1px solid #1C5A72; border-radius: 10px; }
#v65ThemeSearch {
    background: #062F45; color: #F4FAFD; border: 1px solid #2A6179;
    border-radius: 8px; padding: 8px 10px;
}
#v65ThemeSearch::placeholder { color: #89AAB9; }
QListWidget#v65Themes {
    background: transparent; border: 0; outline: none; padding: 2px;
}
QListWidget#v65Themes::item {
    color: #DDECF3; background: transparent; border-radius: 7px;
    padding: 7px 8px; margin: 1px 0; min-height: 20px;
}
QListWidget#v65Themes::item:hover { background: #0D506E; color: #FFFFFF; }
QListWidget#v65Themes::item:selected { background: #0B78B5; color: #FFFFFF; font-weight: 700; }
QPushButton#v65AddTheme {
    background: #0A5878; color: #FFFFFF; border: 1px solid #34758E;
    border-radius: 8px; padding: 8px 10px; font-weight: 600; min-height: 34px;
}
QPushButton#v65AddTheme:hover { background: #0C698E; }

/* ===== overview KPI strip ===== */
#v65Overview {
    background: #FFFFFF; border: 1px solid #DCE5EA; border-radius: 12px;
}
#v65OverviewCaption { color: #71828C; font-size: 8pt; font-weight: 700; letter-spacing: 1px; }
QFrame#v65Kpi {
    background: #F7F9FA; border: 1px solid #E2E9ED; border-radius: 9px;
}
QFrame#v65Kpi:hover { background: #F0F6F9; border-color: #BCD5E1; }
QLabel#v65KpiLabel { color: #627581; font-size: 8pt; font-weight: 600; }
QLabel#v65KpiCount { color: #0B6EAA; font-size: 14pt; font-weight: 700; }

/* ===== workspace ===== */
#v65Workspace { background: #F5F7F9; }
#v65PageTitle { color: #153B55; font-size: 23pt; font-weight: 700; }
#v65PageSubtitle { color: #74838D; font-size: 10pt; }
#v65Toolbar {
    background: #FFFFFF; border: 1px solid #DEE7EC; border-radius: 11px;
}
QPushButton#v65Tab {
    background: transparent; border: 0; color: #657680; border-radius: 7px;
    padding: 8px 12px; font-weight: 600;
}
QPushButton#v65Tab:hover { background: #EFF5F8; color: #075C8A; }
QPushButton#v65Tab[active="true"] { background: #E5F1F7; color: #005C8D; font-weight: 700; }
QLineEdit#v65Filter, QComboBox#v65Filter {
    background: #F8FAFB; border: 1px solid #DCE5EA; border-radius: 8px;
    padding: 8px 10px;
}
QLineEdit#v65Filter:focus, QComboBox#v65Filter:focus { background: #FFFFFF; border-color: #58A5C8; }
QPushButton#v65Tool {
    background: #FFFFFF; color: #294554; border: 1px solid #D7E2E7;
    border-radius: 8px; padding: 8px 11px; font-weight: 600;
}
QPushButton#v65Tool:hover { background: #F2F6F8; }

/* ===== task/detail surfaces ===== */
.card {
    background: #FFFFFF; border: 1px solid #DCE5EA; border-radius: 12px;
}
QTableWidget {
    background: #FFFFFF; alternate-background-color: #FAFCFD;
    border: 0; gridline-color: transparent; outline: none;
}
QTableWidget::item { padding: 9px 10px; border-bottom: 1px solid #EDF1F3; }
QTableWidget::item:hover { background: #F4F9FB; }
QTableWidget::item:selected { background: #E7F2F8; color: #173A52; }
QHeaderView::section {
    background: #F7F9FA; color: #6A7B85; border: 0;
    border-bottom: 1px solid #DCE5EA; padding: 10px; font-size: 8.5pt; font-weight: 700;
}
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background: #FFFFFF; color: #173247; border: 1px solid #D5E0E6;
    border-radius: 8px; padding: 8px 10px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus { border-color: #1689C5; }
QPushButton#primary {
    background: #0050A4; color: #FFFFFF; border: 0; border-radius: 8px;
    padding: 10px 16px; font-weight: 700;
}
QPushButton#primary:hover { background: #0069C8; }
QPushButton#soft {
    background: #FFFFFF; color: #294353; border: 1px solid #D5E0E7;
    border-radius: 8px; padding: 9px 12px;
}
QPushButton#soft:hover { background: #F1F6F9; }

/* ===== boards / lists ===== */
QListWidget {
    background: #F8FAFB; border: 1px solid #E0E8ED; border-radius: 9px;
    outline: none; padding: 5px;
}
QListWidget::item {
    background: #FFFFFF; border: 1px solid #E5ECEF; border-radius: 8px;
    padding: 9px 10px; margin: 3px 1px;
}
QListWidget::item:hover { background: #F3F9FC; border-color: #C7DCE6; }
QListWidget::item:selected { background: #E8F3F8; color: #153B55; border-color: #A7CBDC; }
StatusBadge, ThemeBadge { border-radius: 8px; padding: 5px 10px; font-weight: 600; }
PriorityCard { min-height: 88px; border-radius: 10px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 17px; height: 17px; }

/* ===== themes workspace ===== */
#themesPage { background: #F5F7F9; }
#themesPageTitle { color: #153B55; font-size: 23pt; font-weight: 700; }
#themesPageSubtitle { color: #74838D; }
#themeTile { background: #FFFFFF; border: 1px solid #DCE5EA; border-radius: 12px; }
#themeTile:hover { border-color: #A9CBDC; }
#themeTileName { color: #153B55; font-size: 12pt; font-weight: 700; }
#themeTileMeta { color: #71818C; font-size: 9pt; }
QMenu { background: #FFFFFF; border: 1px solid #DCE5EA; border-radius: 9px; padding: 5px; }
QMenu::item { padding: 8px 24px 8px 10px; border-radius: 6px; }
QMenu::item:selected { background: #EAF4FA; color: #0050A4; }
QScrollBar:vertical { width: 8px; background: transparent; margin: 2px; }
QScrollBar::handle:vertical { background: #A7BAC5; border-radius: 4px; min-height: 26px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QToolTip { background: #163A55; color: #FFFFFF; border: 0; padding: 6px 8px; }
"""


def _move_widget(widget, parent=None):
    if widget is not None:
        widget.setParent(parent)
    return widget


def _new_nav(window, text, key, active=False):
    b = QPushButton(text)
    b.setObjectName("v65Nav")
    b.setCheckable(True)
    b.setProperty("active", "true" if active else "false")
    b.clicked.connect(lambda _=False, k=key: window.set_view(k))
    return b


def _make_kpi(label_text, count_label, window):
    card = QFrame()
    card.setObjectName("v65Kpi")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(10, 7, 10, 7)
    title = QLabel(label_text)
    title.setObjectName("v65KpiLabel")
    count_label.setObjectName("v65KpiCount")
    count_label.setStyleSheet("")
    lay.addWidget(title)
    lay.addWidget(count_label)
    card.setCursor(Qt.PointingHandCursor)
    card.mousePressEvent = lambda _event, k=("Alle" if label_text == "Alle Aufgaben" else label_text): window.set_overview_scope(k)
    return card


def rebuild_premium_shell(window):
    """Replace the old shell while reusing the existing functional widgets."""
    old_central = window.centralWidget()
    stack = window.stack
    stack.setParent(None)

    # Reuse the existing filter/search widgets so all existing signal wiring stays intact.
    global_search = _move_widget(window.global_search)
    global_search.setObjectName("v65TopSearch")
    global_search.setMaximumWidth(320)
    undo = _move_widget(window.undo_button)

    title = _move_widget(window.title_label)
    title.setObjectName("v65PageTitle")
    title.setStyleSheet("")

    for button in window.scope_buttons.values():
        _move_widget(button)
        button.setObjectName("v65Tab")

    search = _move_widget(window.search); search.setObjectName("v65Filter")
    pfilter = _move_widget(window.pfilter); pfilter.setObjectName("v65Filter")
    sfilter = _move_widget(window.sfilter); sfilter.setObjectName("v65Filter")
    dfilter = _move_widget(window.dfilter); dfilter.setObjectName("v65Filter")
    theme_filter = _move_widget(window.theme_filter); theme_filter.setObjectName("v65Filter")
    theme_filter.setMinimumWidth(170)

    projects = _move_widget(window.projects)
    projects.setObjectName("v65Themes")
    project_search = _move_widget(window.project_search)
    project_search.setObjectName("v65ThemeSearch")
    overview_counts = window.overview_labels

    root = QWidget()
    root.setObjectName("v65Root")
    outer = QVBoxLayout(root)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    top = QFrame()
    top.setObjectName("v65Topbar")
    top.setFixedHeight(72)
    tl = QHBoxLayout(top)
    tl.setContentsMargins(24, 12, 20, 12)
    tl.setSpacing(10)
    brand = QLabel("Arturs Taskmanager")
    brand.setObjectName("v65Brand")
    version = QLabel("V6.5")
    version.setObjectName("v65Version")
    offline = QLabel("●  Lokal · Offline")
    offline.setObjectName("v65Offline")
    tl.addWidget(brand)
    tl.addWidget(version)
    tl.addStretch()
    tl.addWidget(offline)
    tl.addWidget(global_search)
    new = QPushButton("＋  Neue Aufgabe")
    new.setObjectName("primary")
    new.clicked.connect(window.new_task)
    tl.addWidget(new)
    tl.addWidget(undo)
    outer.addWidget(top)

    body = QWidget()
    body_lay = QHBoxLayout(body)
    body_lay.setContentsMargins(0, 0, 0, 0)
    body_lay.setSpacing(0)
    outer.addWidget(body, 1)

    side = QFrame()
    side.setObjectName("v65Sidebar")
    side.setFixedWidth(270)
    sl = QVBoxLayout(side)
    sl.setContentsMargins(12, 14, 12, 12)
    sl.setSpacing(5)

    sec = QLabel("ARBEITSBEREICHE")
    sec.setObjectName("v65SectionLabel")
    sl.addWidget(sec)
    nav = []
    for text, key in [("☷   Aufgaben", "tasks"), ("▥   Kanban", "kanban"), ("▦   Eisenhower", "eisenhower"), ("▣   Planung", "planning"), ("▱   Themengebiete", "themes")]:
        b = _new_nav(window, text, key, key == "tasks")
        sl.addWidget(b)
        nav.append((key, b))
    window.nav = nav

    divider = QFrame(); divider.setObjectName("v65Divider"); sl.addWidget(divider); sl.addSpacing(3)
    sec2 = QLabel("WEITERE BEREICHE"); sec2.setObjectName("v65SectionLabel"); sl.addWidget(sec2)
    for text, slot in [("▧   Berichte & Export", window.export_excel), ("⚙   Einstellungen", lambda: None), ("?   Hilfe & Info", lambda: None)]:
        b = QPushButton(text); b.setObjectName("v65Secondary")
        if "Berichte" in text: b.clicked.connect(slot)
        elif "Einstellungen" in text:
            from PySide6.QtWidgets import QMessageBox
            b.clicked.connect(lambda: QMessageBox.information(window, "Einstellungen", "Lokale Datenbank · Offline-Betrieb · Excel-Export"))
        else:
            from PySide6.QtWidgets import QMessageBox
            b.clicked.connect(lambda: QMessageBox.information(window, "Hilfe & Info", "Aufgabe auswählen, priorisieren und über Kanban verschieben."))
        sl.addWidget(b)
    sl.addSpacing(6)

    theme_panel = QFrame(); theme_panel.setObjectName("v65ThemePanel")
    tp = QVBoxLayout(theme_panel); tp.setContentsMargins(9, 9, 9, 9); tp.setSpacing(6)
    th = QLabel("THEMENGEBIETE"); th.setObjectName("v65SectionLabel"); tp.addWidget(th)
    tp.addWidget(project_search)
    tp.addWidget(projects, 1)
    add_theme = QPushButton("＋  Neues Themengebiet"); add_theme.setObjectName("v65AddTheme"); add_theme.clicked.connect(window.new_project); tp.addWidget(add_theme)
    sl.addWidget(theme_panel, 1)

    overview = QFrame(); overview.setObjectName("v65Overview")
    ov = QVBoxLayout(overview); ov.setContentsMargins(10, 8, 10, 10); ov.setSpacing(6)
    cap = QLabel("ÜBERSICHT"); cap.setObjectName("v65OverviewCaption"); ov.addWidget(cap)
    kpi_row = QHBoxLayout(); kpi_row.setSpacing(5)
    for key, label in [("Heute", "Heute"), ("Diese Woche", "Diese Woche"), ("Später", "Später"), ("Erledigt", "Erledigt"), ("Alle", "Alle Aufgaben")]:
        kpi_row.addWidget(_make_kpi(label, overview_counts[key], window), 1)
    ov.addLayout(kpi_row)
    sl.addWidget(overview)

    body_lay.addWidget(side)

    workspace = QWidget(); workspace.setObjectName("v65Workspace")
    wl = QVBoxLayout(workspace); wl.setContentsMargins(28, 22, 28, 20); wl.setSpacing(12)
    head = QHBoxLayout(); head.addWidget(title); head.addStretch(); wl.addLayout(head)
    subtitle = QLabel("Aufgaben, Prioritäten und Fälligkeiten auf einen Blick")
    subtitle.setObjectName("v65PageSubtitle")
    wl.addWidget(subtitle)

    toolbar = QFrame(); toolbar.setObjectName("v65Toolbar")
    tb = QVBoxLayout(toolbar); tb.setContentsMargins(8, 7, 8, 7); tb.setSpacing(7)
    tabs = QHBoxLayout(); tabs.setSpacing(2)
    for key in ("Heute", "Diese Woche", "Später", "Alle"):
        b = window.scope_buttons[key]
        tabs.addWidget(b)
    tabs.addStretch()
    tabs.addWidget(theme_filter)
    sort = QPushButton("↕  Sortierung"); sort.setObjectName("v65Tool"); sort.clicked.connect(window.cycle_sort); tabs.addWidget(sort)
    tb.addLayout(tabs)
    filters = QHBoxLayout(); filters.setSpacing(7)
    filters.addWidget(search, 1)
    filters.addWidget(pfilter)
    filters.addWidget(sfilter)
    filters.addWidget(dfilter)
    tb.addLayout(filters)
    wl.addWidget(toolbar)

    wl.addWidget(stack, 1)
    body_lay.addWidget(workspace, 1)

    window.setCentralWidget(root)
    window._v65_root = root
    window._v65_old_central = old_central
    window.setMinimumSize(1180, 760)
    window.resize(1540, 940)
    window.refresh_all()
    window.set_view("tasks")
