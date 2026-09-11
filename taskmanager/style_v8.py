"""V8 premium enterprise presentation layer.

The module rebuilds the visible shell around MainWindow's existing functional
widgets. Database and task business logic stays in ui.py/db.py.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget, QSplitter, QToolButton,
    QMenu, QButtonGroup,
)

from .constants import PRIORITIES, PRIORITY_LIGHTS
from .v8_interactions import format_due_date, priority_label, responsive_layout


V8_STYLE = r"""
* { font-family: "Segoe UI"; font-size: 9.5pt; color: #263844; }
QMainWindow, QWidget { background: #F4F7F9; }
#v8Shell { background: #F4F7F9; }
#v8Topbar { background: #FFFFFF; border-bottom: 1px solid #D9E2E8; }
#v8Brand { color: #172B3A; font-size: 14pt; font-weight: 700; }
#v8Meta { color: #71818C; font-size: 8pt; }
#v8Nav { background: #FFFFFF; border-right: 1px solid #D9E2E8; }
#v8NavHeader { color: #7A8992; font-size: 7.5pt; font-weight: 700; letter-spacing: 1px; }
QPushButton#v8NavButton { background: transparent; border: 0; border-radius: 5px; color: #455761; text-align: left; padding: 7px 9px; min-height: 31px; font-weight: 600; }
QPushButton#v8NavButton:hover { background: #F1F5F7; color: #005C8D; }
QPushButton#v8NavButton[active="true"] { background: #E7F1FA; color: #0050A4; font-weight: 700; }
#v8NavFooter { color: #82919A; font-size: 7.5pt; }
#v8Workspace { background: #F4F7F9; }
#v8HeaderTitle { color: #172B3A; font-size: 18pt; font-weight: 700; }
#v8Count { color: #788892; font-size: 8.5pt; }
QPushButton#v8Scope { background: transparent; border: 0; border-bottom: 2px solid transparent; color: #5E707B; padding: 7px 9px; font-weight: 600; }
QPushButton#v8Scope:hover { color: #005C8D; background: #EEF4F7; }
QPushButton#v8Scope[active="true"] { color: #0050A4; border-bottom-color: #0050A4; }
QPushButton#v8Tool { background: #FFFFFF; border: 1px solid #D4DEE4; border-radius: 5px; color: #4A5E69; padding: 6px 9px; font-weight: 600; }
QPushButton#v8Tool:hover { background: #F2F6F8; border-color: #B7C8D2; }
QPushButton#v8Primary { background: #0050A4; color: #FFFFFF; border: 0; border-radius: 6px; padding: 8px 14px; font-weight: 700; }
QPushButton#v8Primary:hover { background: #0068C9; }
QPushButton#v8Primary:pressed { background: #00458F; }
#v8TaskSurface { background: #FFFFFF; border: 1px solid #DCE4E9; border-radius: 6px; }
#v8Inspector { background: #FFFFFF; border-left: 1px solid #D9E2E8; }
#v8InspectorTitle { color: #172B3A; font-size: 11pt; font-weight: 700; }
#v8InspectorMeta { color: #75858F; font-size: 8pt; }
#v8Chip { background: #E7F1FA; color: #0050A4; border-radius: 10px; padding: 3px 7px; font-size: 8pt; font-weight: 600; }
#v8Divider { background: #E4EAEE; min-height: 1px; max-height: 1px; }
QListWidget#v8Themes { background: transparent; border: 0; outline: none; }
QListWidget#v8Themes::item { color: #53656F; padding: 5px 7px; border-radius: 4px; margin: 1px 0; }
QListWidget#v8Themes::item:hover { background: #F1F5F7; color: #005C8D; }
QListWidget#v8Themes::item:selected { background: #E7F1FA; color: #0050A4; font-weight: 700; }
QFrame#v8TaskFrame { background: #FFFFFF; border: 1px solid #E0E7EB; border-radius: 6px; }
QFrame#v8TaskFrame:hover { border-color: #B8CCD8; }
QLabel#v8TaskTitle { color: #263844; font-size: 9.5pt; font-weight: 600; }
QLabel#v8TaskMeta { color: #788992; font-size: 8pt; }
QLabel#v8Due { color: #526873; font-size: 8pt; }
QLabel#v8Overdue { color: #B3261E; font-size: 8pt; font-weight: 700; }
QLabel#v8Priority { color: #526873; font-size: 8pt; }
QToolButton#v8Icon { background: transparent; border: 0; border-radius: 4px; padding: 4px; color: #637681; }
QToolButton#v8Icon:hover { background: #EAF2F7; color: #0050A4; }
QLineEdit, QComboBox, QDateEdit, QTextEdit { background: #FFFFFF; border: 1px solid #D4DEE4; border-radius: 5px; padding: 6px 8px; }
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus { border-color: #1689C5; }
QScrollBar:vertical { width: 7px; background: transparent; }
QScrollBar::handle:vertical { background: #B8C6CD; border-radius: 3px; min-height: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QToolTip { background: #172B3A; color: #FFFFFF; border: 0; padding: 5px 7px; }
"""


_NAV = [
    ("▤", "Aufgaben", "tasks"),
    ("◷", "Heute", "today"),
    ("▥", "Diese Woche", "week"),
    ("›", "Später", "later"),
    ("✓", "Erledigt", "done"),
]
_VIEWS = [("▦", "Kanban", "kanban"), ("⊞", "Eisenhower", "eisenhower"), ("▣", "Planung", "planning")]


def _set_property(widget, name, value):
    widget.setProperty(name, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def _priority_text(priority):
    return priority_label(priority)


def _priority_indicator(priority):
    lights = PRIORITY_LIGHTS.get(priority, ("gray", "gray", "gray"))
    chars = {"red": "●", "yellow": "●", "green": "●", "gray": "○"}
    return " ".join(chars[x] for x in lights)


def _make_nav_button(window, icon, text, key):
    button = QPushButton(f"{icon}   {text}")
    button.setObjectName("v8NavButton")
    button.setCheckable(True)
    button.setToolTip(text)
    button.clicked.connect(lambda _=False, k=key: _navigate(window, k))
    button._v8_full_text = f"{icon}   {text}"
    button._v8_icon = icon
    return button


def _navigate(window, key):
    if key in {"tasks", "today", "week", "later", "done"}:
        if key == "today":
            window.set_view("tasks"); window.set_scope("Heute")
        elif key == "week":
            window.set_view("tasks"); window.set_scope("Diese Woche")
        elif key == "later":
            window.set_view("tasks"); window.set_scope("Später")
        elif key == "done":
            window.set_view("tasks"); window.set_scope("Erledigt")
        else:
            window.set_view("tasks"); window.set_scope("Alle")
    else:
        window.set_view(key)
    _sync_active_nav(window, key)


def _sync_active_nav(window, key):
    for item_key, button in getattr(window, "_v8_nav_items", []):
        active = item_key == key
        _set_property(button, "active", "true" if active else "false")
        button.setChecked(active)


def _toggle_navigation(window):
    collapsed = not getattr(window, "_v8_nav_collapsed", False)
    window._v8_nav_collapsed = collapsed
    width = 60 if collapsed else 228
    window._v8_nav.setFixedWidth(width)
    for _, button in window._v8_nav_items:
        button.setText(button._v8_icon if collapsed else button._v8_full_text)
        button.setToolTip(button._v8_full_text.replace(button._v8_icon + "   ", ""))
    window._v8_nav_header.setVisible(not collapsed)
    window._v8_theme_label.setVisible(not collapsed)
    window._v8_themes.setVisible(not collapsed)
    window._v8_theme_add.setVisible(not collapsed)


def _toggle_detail(window):
    inspector = getattr(window, "editor", None)
    if inspector is None:
        return
    window._v8_detail_open = not getattr(window, "_v8_detail_open", True)
    inspector.setVisible(window._v8_detail_open)
    parent = inspector.parentWidget()
    if parent is not None and hasattr(parent, "setSizes"):
        if window._v8_detail_open:
            parent.setSizes([max(450, parent.width() - window._v8_detail_width), window._v8_detail_width])
        else:
            parent.setSizes([max(450, parent.width()), 0])


def _sync_detail_from_selection(window):
    table = getattr(window, "table", None)
    if table is None:
        return
    has_selection = bool(table.selectionModel() and table.selectionModel().hasSelection())
    if has_selection and not getattr(window, "_v8_detail_open", False):
        window._v8_detail_open = True
        if getattr(window, "editor", None) is not None:
            window.editor.setVisible(True)
    if has_selection:
        window._v8_selected_id = getattr(window, "selected_task", None)


def _install_scope_row(window, parent_layout):
    row = QHBoxLayout(); row.setSpacing(2)
    window._v8_scopes = []
    for text, key in [("Alle Aufgaben", "Alle"), ("Heute", "Heute"), ("Diese Woche", "Diese Woche"), ("Später", "Später"), ("Erledigt", "Erledigt")]:
        b = QPushButton(text); b.setObjectName("v8Scope"); b.setCheckable(True); b.setToolTip(text)
        b.clicked.connect(lambda _=False, k=key: window.set_scope(k))
        row.addWidget(b); window._v8_scopes.append((key, b))
    row.addStretch(1)
    filter_b = QPushButton("Filter"); filter_b.setObjectName("v8Tool"); filter_b.setToolTip("Aufgaben filtern")
    filter_b.clicked.connect(lambda: _show_filter_menu(window, filter_b)); row.addWidget(filter_b)
    sort_b = QPushButton("Sortieren"); sort_b.setObjectName("v8Tool"); sort_b.clicked.connect(window.cycle_sort); row.addWidget(sort_b)
    group_b = QPushButton("Gruppieren"); group_b.setObjectName("v8Tool"); group_b.clicked.connect(lambda: _show_group_menu(window, group_b)); row.addWidget(group_b)
    compact = QPushButton("Liste / Kompakt"); compact.setObjectName("v8Tool"); compact.clicked.connect(lambda: _toggle_compact(window)); row.addWidget(compact)
    parent_layout.addLayout(row)


def _show_filter_menu(window, anchor):
    menu = QMenu(anchor)
    for label, widget_name in [("Status", "sfilter"), ("Priorität", "pfilter"), ("Fälligkeit", "dfilter"), ("Themengebiet", "theme_filter")]:
        widget = getattr(window, widget_name, None)
        if widget is None:
            continue
        submenu = menu.addMenu(label)
        for index in range(widget.count()):
            action = submenu.addAction(widget.itemText(index))
            action.setCheckable(True); action.setChecked(index == widget.currentIndex())
            action.triggered.connect(lambda checked=False, w=widget, i=index: w.setCurrentIndex(i))
    menu.exec(anchor.mapToGlobal(anchor.rect().bottomLeft()))


def _show_group_menu(window, anchor):
    menu = QMenu(anchor)
    for label in ["Keine Gruppierung", "Themengebiet", "Priorität", "Fälligkeit", "Status"]:
        action = menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(label == getattr(window, "_v8_group", "Keine Gruppierung"))
        action.triggered.connect(lambda checked=False, x=label: _set_group(window, x))
    menu.exec(anchor.mapToGlobal(anchor.rect().bottomLeft()))


def _set_group(window, group):
    window._v8_group = group
    if hasattr(window, "refresh_all"):
        window.refresh_all()


def _toggle_compact(window):
    compact = not getattr(window, "_v8_compact", False)
    window._v8_compact = compact
    table = getattr(window, "table", None)
    if table is not None:
        table.verticalHeader().setDefaultSectionSize(30 if compact else 42)


def _build_navigation(window, root_layout):
    nav = QFrame(); nav.setObjectName("v8Nav"); nav.setFixedWidth(228)
    layout = QVBoxLayout(nav); layout.setContentsMargins(10, 10, 10, 10); layout.setSpacing(2)
    top = QHBoxLayout(); top.setSpacing(4)
    collapse = QToolButton(); collapse.setText("☰"); collapse.setObjectName("v8Icon"); collapse.setToolTip("Navigation ein-/ausklappen"); collapse.clicked.connect(lambda: _toggle_navigation(window)); top.addWidget(collapse)
    header = QLabel("ARBEITSBEREICH"); header.setObjectName("v8NavHeader"); top.addWidget(header); top.addStretch(); layout.addLayout(top)
    window._v8_nav_header = header
    window._v8_nav_items = []
    for icon, text, key in _NAV:
        button = _make_nav_button(window, icon, text, key); layout.addWidget(button); window._v8_nav_items.append((key, button))
    divider = QFrame(); divider.setObjectName("v8Divider"); layout.addWidget(divider); layout.addSpacing(4)
    views_label = QLabel("ANSICHTEN"); views_label.setObjectName("v8NavHeader"); layout.addWidget(views_label)
    for icon, text, key in _VIEWS:
        button = _make_nav_button(window, icon, text, key); layout.addWidget(button); window._v8_nav_items.append((key, button))
    divider2 = QFrame(); divider2.setObjectName("v8Divider"); layout.addWidget(divider2); layout.addSpacing(4)
    theme_label = QLabel("THEMENGEBIETE"); theme_label.setObjectName("v8NavHeader"); layout.addWidget(theme_label); window._v8_theme_label = theme_label
    themes = QListWidget(); themes.setObjectName("v8Themes"); themes.setMaximumHeight(210); layout.addWidget(themes, 1); window._v8_themes = themes
    add_theme = QPushButton("＋  Neues Themengebiet"); add_theme.setObjectName("v8Tool"); add_theme.clicked.connect(window.new_project); layout.addWidget(add_theme); window._v8_theme_add = add_theme
    footer = QLabel("Lokal · Offline"); footer.setObjectName("v8NavFooter"); layout.addWidget(footer)
    window._v8_nav = nav
    root_layout.addWidget(nav)

    def refresh_themes():
        themes.clear()
        source = getattr(window, "projects", None)
        if source is None:
            return
        for i in range(source.count()):
            item = source.item(i)
            pid = item.data(Qt.UserRole)
            if pid is None:
                continue
            visible = QListWidgetItem(item.text().replace("▦  ", "", 1)); visible.setData(Qt.UserRole, pid); themes.addItem(visible)
        themes.itemClicked.connect(lambda item: window.set_project(item.data(Qt.UserRole))) if themes.count() and themes.receivers(themes.itemClicked) == 0 else None
    window._v8_refresh_themes = refresh_themes


def _install_task_surface(window, workspace_layout):
    # Reuse the existing functional task page, but give it the V8 surface and
    # keep its editor as the common inspector across the task-oriented views.
    stack = getattr(window, "stack", None)
    if stack is None:
        return
    stack.setObjectName("v8TaskSurface")
    workspace_layout.addWidget(stack, 1)
    table = getattr(window, "table", None)
    if table is not None:
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setWordWrap(False)
        table.verticalHeader().setDefaultSectionSize(42)
        table.setTextElideMode(Qt.ElideRight)
        table.horizontalHeader().setStretchLastSection(False)
        fixed = {0: 34, 2: 118, 3: 88, 4: 96, 5: 84, 6: 34}
        table.horizontalHeader().setSectionResizeMode(0, table.horizontalHeader().Fixed)
        table.horizontalHeader().setSectionResizeMode(1, table.horizontalHeader().Stretch)
        for col, width in fixed.items():
            table.horizontalHeader().setSectionResizeMode(col, table.horizontalHeader().Fixed)
            table.setColumnWidth(col, width)
        table.itemSelectionChanged.connect(lambda: _sync_detail_from_selection(window))

    editor = getattr(window, "editor", None)
    if editor is not None:
        editor.setObjectName("v8Inspector")
        window._v8_detail_width = 380
        window._v8_detail_open = False
        editor.setVisible(False)
        parent = editor.parentWidget()
        if parent is not None:
            parent.setChildrenCollapsible(False)
            parent.setHandleWidth(5)
            parent.setStretchFactor(0, 1)
            parent.setStretchFactor(1, 0)
            parent.setSizes([max(450, parent.width() - 380), 380])
            editor.setMinimumWidth(320)
            editor.setMaximumWidth(650)
            editor.setVisible(False)
        table.itemSelectionChanged.connect(lambda: _show_selected_editor(window)) if table is not None else None


def _show_selected_editor(window):
    table = getattr(window, "table", None)
    if table is None or not table.selectionModel() or not table.selectionModel().hasSelection():
        return
    editor = getattr(window, "editor", None)
    if editor is not None:
        editor.setVisible(True)
        window._v8_detail_open = True
        parent = editor.parentWidget()
        if parent is not None and hasattr(parent, "setSizes"):
            parent.setSizes([max(450, parent.width() - window._v8_detail_width), window._v8_detail_width])


def _install_title_and_toolbar(window, layout):
    header = QHBoxLayout(); header.setSpacing(10)
    title_box = QVBoxLayout(); title_box.setSpacing(1)
    title = QLabel("Aufgaben"); title.setObjectName("v8HeaderTitle"); title_box.addWidget(title)
    count = QLabel("0 Aufgaben"); count.setObjectName("v8Count"); title_box.addWidget(count)
    window._v8_count = count
    header.addLayout(title_box); header.addStretch()
    inspector = QPushButton("Detail"); inspector.setObjectName("v8Tool"); inspector.setToolTip("Detailpanel ein-/ausblenden"); inspector.clicked.connect(lambda: _toggle_detail(window)); header.addWidget(inspector)
    primary = QPushButton("＋  Aufgabe"); primary.setObjectName("v8Primary"); primary.clicked.connect(window.new_task); header.addWidget(primary)
    layout.addLayout(header)
    _install_scope_row(window, layout)


def _style_existing_widgets(window):
    table = getattr(window, "table", None)
    if table is not None:
        table.setStyleSheet("QTableWidget{background:#FFFFFF;border:0;} QTableWidget::item{padding:6px 7px;border-bottom:1px solid #EEF2F4;} QTableWidget::item:selected{background:#E7F1FA;color:#172B3A;} QHeaderView::section{background:#FFFFFF;border:0;border-bottom:1px solid #DCE4E9;padding:7px;color:#74838C;font-size:8pt;font-weight:700;}")
    editor = getattr(window, "editor", None)
    if editor is not None:
        editor.setStyleSheet("QFrame#v8Inspector{background:#FFFFFF;border-left:1px solid #D9E2E8;} QLabel{color:#536670;} QPushButton#primary{background:#0050A4;color:white;border:0;border-radius:5px;padding:7px 10px;font-weight:700;} QPushButton#soft{background:#FFFFFF;color:#455A65;border:1px solid #D4DEE4;border-radius:5px;padding:6px 9px;}")


def rebuild_v8_shell(window):
    """Replace the visible V7 shell with the V8 shell."""
    old = window.centralWidget()
    if old is not None:
        old.setParent(None)
    root = QWidget(); root.setObjectName("v8Shell")
    outer = QVBoxLayout(root); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)

    top = QFrame(); top.setObjectName("v8Topbar"); top.setFixedHeight(52)
    tl = QHBoxLayout(top); tl.setContentsMargins(14, 7, 14, 7); tl.setSpacing(8)
    brand = QLabel("Arturs Taskmanager"); brand.setObjectName("v8Brand"); tl.addWidget(brand)
    version = QLabel("V8.0"); version.setObjectName("v8Meta"); tl.addWidget(version)
    offline = QLabel("● Lokal · Offline"); offline.setObjectName("v8Meta"); tl.addWidget(offline); tl.addStretch()
    search = getattr(window, "global_search", None)
    if search is not None:
        search.setMaximumWidth(280); search.setPlaceholderText("Suche  ·  Strg + F"); tl.addWidget(search)
    undo = getattr(window, "undo_button", None)
    if undo is not None:
        undo.setObjectName("v8Tool"); tl.addWidget(undo)
    nav_toggle = QToolButton(); nav_toggle.setText("☰"); nav_toggle.setObjectName("v8Icon"); nav_toggle.setToolTip("Navigation ein-/ausklappen")
    tl.addWidget(nav_toggle)
    outer.addWidget(top)

    body = QWidget(); body_l = QHBoxLayout(body); body_l.setContentsMargins(0, 0, 0, 0); body_l.setSpacing(0); outer.addWidget(body, 1)
    _build_navigation(window, body_l)
    nav_toggle.clicked.connect(lambda: _toggle_navigation(window))

    workspace = QWidget(); workspace.setObjectName("v8Workspace"); wl = QVBoxLayout(workspace); wl.setContentsMargins(18, 14, 18, 14); wl.setSpacing(9)
    _install_title_and_toolbar(window, wl)
    _install_task_surface(window, wl)
    body_l.addWidget(workspace, 1)

    window.setCentralWidget(root)
    window._v8_workspace = workspace
    window._v8_shell = root
    window._v8_nav_collapsed = False
    window._v8_group = "Keine Gruppierung"
    _style_existing_widgets(window)
    _sync_active_nav(window, "tasks")
    QTimer.singleShot(0, lambda: _v8_refresh(window))
    return root


def _v8_refresh(window):
    if hasattr(window, "_v8_refresh_themes"):
        window._v8_refresh_themes()
    count = getattr(window, "_v8_count", None)
    table = getattr(window, "table", None)
    if count is not None and table is not None:
        count.setText(f"{table.rowCount()} Aufgaben")
    for key, button in getattr(window, "_v8_scopes", []):
        _set_property(button, "active", "true" if getattr(window, "scope", "Alle") == key else "false")
        button.setChecked(getattr(window, "scope", "Alle") == key)


def install_v8_responsive_behavior(window):
    if getattr(window, "_v8_responsive_installed", False):
        return
    original_resize = window.resizeEvent

    def resize_event(event):
        original_resize(event)
        state = responsive_layout(window.width(), getattr(window, "_v8_detail_open", False), getattr(window, "_v8_nav_collapsed", False))
        if state["nav_collapsed"] and not getattr(window, "_v8_nav_collapsed", False):
            _toggle_navigation(window)
        editor = getattr(window, "editor", None)
        if editor is not None:
            editor.setVisible(state["detail_visible"])
        if not state["detail_visible"]:
            window._v8_detail_open = False
    window.resizeEvent = resize_event
    window._v8_responsive_installed = True
