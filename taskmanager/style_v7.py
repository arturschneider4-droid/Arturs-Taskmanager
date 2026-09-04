"""V7 professional desktop shell.

The shell is intentionally quiet and task-first: compact navigation on the
left, a clean workspace in the center, and the existing task detail editor
inside the task workspace. Business logic remains in ui.py/db.py.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


V7_STYLE = r"""
* { font-family: "Segoe UI"; font-size: 10pt; color: #253746; }
QMainWindow, QWidget { background: #F6F8FA; }

#v7Topbar { background: #FFFFFF; border-bottom: 1px solid #DCE3E8; }
#v7Brand { color: #173A55; font-size: 15pt; font-weight: 700; }
#v7Version { color: #74828B; font-size: 8pt; font-weight: 600; padding: 3px 6px; }
#v7Offline { color: #687984; font-size: 8.5pt; }
#v7TopSearch { background: #F5F7F9; border: 1px solid #D9E1E6; border-radius: 6px; padding: 7px 10px; }
#v7TopSearch:focus { background: #FFFFFF; border-color: #78AFC8; }

#v7Sidebar { background: #FFFFFF; border-right: 1px solid #DCE3E8; }
#v7NavHeader { color: #7A8992; font-size: 8pt; font-weight: 700; letter-spacing: 1px; padding: 4px 8px 6px; }
QPushButton#v7Nav { background: transparent; border: 0; border-radius: 6px; color: #445762; text-align: left; padding: 8px 10px; min-height: 34px; font-weight: 600; }
QPushButton#v7Nav:hover { background: #F0F5F8; color: #075C8A; }
QPushButton#v7Nav[active="true"] { background: #E8F2F7; color: #005C8D; font-weight: 700; }
#v7Divider { background: #E3E9ED; min-height: 1px; max-height: 1px; }
#v7ThemesLabel { color: #84919A; font-size: 8pt; font-weight: 700; letter-spacing: .8px; }
QListWidget#v7Themes { background: transparent; border: 0; outline: none; }
QListWidget#v7Themes::item { color: #52636D; border-radius: 5px; padding: 6px 8px; margin: 1px 0; }
QListWidget#v7Themes::item:hover { background: #F1F5F7; color: #075C8A; }
QListWidget#v7Themes::item:selected { background: #E8F2F7; color: #005C8D; font-weight: 700; }
QPushButton#v7AddTheme { background: #FFFFFF; border: 1px solid #D4DEE4; border-radius: 6px; color: #3E5663; padding: 7px 9px; font-weight: 600; }
QPushButton#v7AddTheme:hover { background: #F4F8FA; border-color: #AFC8D6; }
#v7SidebarFooter { color: #87959D; font-size: 8pt; }

#v7Workspace { background: #F6F8FA; }
#v7PageHeader { background: transparent; }
#v7PageTitle { color: #173A55; font-size: 20pt; font-weight: 700; }
#v7PageSubtitle { color: #788790; font-size: 9.5pt; }
#v7ScopeBar { background: #FFFFFF; border: 1px solid #DCE4E9; border-radius: 7px; }
QPushButton#v7Scope { background: transparent; border: 0; border-radius: 5px; color: #667680; padding: 7px 11px; font-weight: 600; }
QPushButton#v7Scope:hover { background: #F1F5F7; color: #075C8A; }
QPushButton#v7Scope[active="true"] { background: #E9F2F7; color: #005C8D; }
QLineEdit#v7Filter, QComboBox#v7Filter { background: #FFFFFF; border: 1px solid #D5DFE5; border-radius: 6px; padding: 7px 9px; }
QLineEdit#v7Filter:focus, QComboBox#v7Filter:focus { border-color: #78AFC8; }
QPushButton#v7Tool { background: #FFFFFF; border: 1px solid #D5DFE5; border-radius: 6px; padding: 7px 10px; color: #425762; font-weight: 600; }
QPushButton#v7Tool:hover { background: #F2F6F8; }

#v7Detail { background: #FFFFFF; border: 1px solid #DCE4E9; border-radius: 8px; }
.card { background: #FFFFFF; border: 1px solid #DCE4E9; border-radius: 8px; }
QTableWidget { background: #FFFFFF; border: 0; gridline-color: transparent; outline: none; }
QTableWidget::item { padding: 8px 9px; border-bottom: 1px solid #EEF2F4; }
QTableWidget::item:hover { background: #F7FAFC; }
QTableWidget::item:selected { background: #EAF3F8; color: #173A55; }
QHeaderView::section { background: #FFFFFF; color: #7A8992; border: 0; border-bottom: 1px solid #DCE4E9; padding: 8px 9px; font-size: 8pt; font-weight: 700; }
QLineEdit, QComboBox, QDateEdit, QTextEdit { background: #FFFFFF; color: #253746; border: 1px solid #D4DEE4; border-radius: 6px; padding: 7px 9px; }
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus { border-color: #1689C5; }
QPushButton#primary { background: #0050A4; color: #FFFFFF; border: 0; border-radius: 6px; padding: 8px 13px; font-weight: 700; }
QPushButton#primary:hover { background: #0068C9; }
QPushButton#soft { background: #FFFFFF; color: #425762; border: 1px solid #D4DEE4; border-radius: 6px; padding: 7px 10px; }
QPushButton#soft:hover { background: #F2F6F8; }
QPushButton#v7New { background: #0050A4; color: #FFFFFF; border: 0; border-radius: 6px; padding: 8px 13px; font-weight: 700; }
QPushButton#v7New:hover { background: #0068C9; }

QListWidget { background: #FFFFFF; border: 1px solid #DCE4E9; border-radius: 7px; outline: none; padding: 4px; }
QListWidget::item { background: #FFFFFF; border: 1px solid #E7ECEF; border-radius: 6px; padding: 8px 9px; margin: 2px 1px; }
QListWidget::item:hover { background: #F6FAFC; }
QListWidget::item:selected { background: #EAF3F8; border-color: #B7D3E1; color: #173A55; }
QCheckBox { spacing: 7px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QMenu { background: #FFFFFF; border: 1px solid #DCE4E9; border-radius: 7px; padding: 4px; }
QMenu::item { padding: 7px 20px 7px 9px; border-radius: 4px; }
QMenu::item:selected { background: #EAF3F8; color: #005C8D; }
QScrollBar:vertical { width: 8px; background: transparent; margin: 1px; }
QScrollBar::handle:vertical { background: #B5C4CC; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QToolTip { background: #173A55; color: #FFFFFF; border: 0; padding: 5px 7px; }
"""


def _nav_button(window, text, key):
    button = QPushButton(text)
    button.setObjectName("v7Nav")
    button.setCheckable(True)
    button.clicked.connect(lambda _=False, k=key: window.set_view(k))
    return button


def _set_active(window, key):
    for item_key, button in getattr(window, "nav", []):
        active = item_key == key
        button.setProperty("active", "true" if active else "false")
        button.setChecked(active)
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()


def rebuild_professional_shell(window):
    """Build the V7 shell around existing functional widgets."""
    old = window.centralWidget()
    if old is not None:
        old.setParent(None)

    global_search = window.global_search
    global_search.setObjectName("v7TopSearch")
    global_search.setMaximumWidth(300)
    undo = window.undo_button
    undo.setObjectName("soft")

    root = QWidget()
    outer = QVBoxLayout(root)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    top = QFrame()
    top.setObjectName("v7Topbar")
    top.setFixedHeight(56)
    tl = QHBoxLayout(top)
    tl.setContentsMargins(18, 8, 16, 8)
    tl.setSpacing(9)
    brand = QLabel("Arturs Taskmanager")
    brand.setObjectName("v7Brand")
    version = QLabel("V7.0")
    version.setObjectName("v7Version")
    offline = QLabel("● Lokal · Offline")
    offline.setObjectName("v7Offline")
    tl.addWidget(brand)
    tl.addWidget(version)
    tl.addSpacing(8)
    tl.addWidget(offline)
    tl.addStretch()
    tl.addWidget(global_search)
    new_task = QPushButton("＋  Neue Aufgabe")
    new_task.setObjectName("v7New")
    new_task.clicked.connect(window.new_task)
    tl.addWidget(new_task)
    tl.addWidget(undo)
    outer.addWidget(top)

    body = QWidget()
    body_lay = QHBoxLayout(body)
    body_lay.setContentsMargins(0, 0, 0, 0)
    body_lay.setSpacing(0)

    sidebar = QFrame()
    sidebar.setObjectName("v7Sidebar")
    sidebar.setFixedWidth(214)
    sl = QVBoxLayout(sidebar)
    sl.setContentsMargins(12, 16, 12, 12)
    sl.setSpacing(3)

    nav_header = QLabel("ARBEITSBEREICHE")
    nav_header.setObjectName("v7NavHeader")
    sl.addWidget(nav_header)
    window.nav = []
    for text, key in [("Aufgaben", "tasks"), ("Kanban", "kanban"), ("Eisenhower", "eisenhower"), ("Planung", "planning"), ("Themengebiete", "themes")]:
        button = _nav_button(window, text, key)
        sl.addWidget(button)
        window.nav.append((key, button))

    divider = QFrame()
    divider.setObjectName("v7Divider")
    sl.addWidget(divider)
    sl.addSpacing(6)

    themes_label = QLabel("THEMENGEBIETE")
    themes_label.setObjectName("v7ThemesLabel")
    sl.addWidget(themes_label)
    projects = window.projects
    projects.setObjectName("v7Themes")
    sl.addWidget(projects, 1)
    add_theme = QPushButton("＋  Neues Themengebiet")
    add_theme.setObjectName("v7AddTheme")
    add_theme.clicked.connect(window.new_project)
    sl.addWidget(add_theme)
    footer = QLabel("Lokale Datenbank  ·  Offline")
    footer.setObjectName("v7SidebarFooter")
    sl.addWidget(footer)
    body_lay.addWidget(sidebar)

    workspace = QWidget()
    workspace.setObjectName("v7Workspace")
    wl = QVBoxLayout(workspace)
    wl.setContentsMargins(24, 18, 24, 18)
    wl.setSpacing(10)

    header = QWidget()
    header.setObjectName("v7PageHeader")
    hl = QHBoxLayout(header)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.setSpacing(4)
    title = window.title_label
    title.setObjectName("v7PageTitle")
    title.setStyleSheet("")
    hl.addWidget(title)
    hl.addStretch()
    wl.addWidget(header)

    scope = QFrame()
    scope.setObjectName("v7ScopeBar")
    scope_lay = QHBoxLayout(scope)
    scope_lay.setContentsMargins(4, 4, 4, 4)
    scope_lay.setSpacing(2)
    for key, button in window.scope_buttons.items():
        button.setObjectName("v7Scope")
        button.setProperty("active", "true" if key == "Alle" else "false")
        button.style().unpolish(button); button.style().polish(button)
        scope_lay.addWidget(button)
    scope_lay.addStretch()
    theme_filter = window.theme_filter
    theme_filter.setObjectName("v7Filter")
    theme_filter.setMinimumWidth(160)
    scope_lay.addWidget(theme_filter)
    sort = getattr(window, "_v7_sort_button", None)
    if sort is None:
        sort = QPushButton("↕  Sortierung")
        sort.setObjectName("v7Tool")
        sort.clicked.connect(window.cycle_sort)
        window._v7_sort_button = sort
    scope_lay.addWidget(sort)
    wl.addWidget(scope)

    filters = QHBoxLayout()
    filters.setSpacing(7)
    for widget, width in [(window.search, 0), (window.pfilter, 145), (window.sfilter, 125), (window.dfilter, 145)]:
        widget.setObjectName("v7Filter")
        if width:
            widget.setFixedWidth(width)
        filters.addWidget(widget, 1 if width == 0 else 0)
    wl.addLayout(filters)

    stack = window.stack
    stack.setParent(workspace)
    wl.addWidget(stack, 1)
    body_lay.addWidget(workspace, 1)
    outer.addWidget(body, 1)

    # Keep the existing task editor as the right-hand detail surface.
    if hasattr(window, "editor"):
        window.editor.setObjectName("v7Detail")

    window.setCentralWidget(root)
    _set_active(window, "tasks")
    window.set_view("tasks")
