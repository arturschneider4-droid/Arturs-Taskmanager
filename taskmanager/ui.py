from datetime import date, datetime, timedelta

from PySide6.QtCore import Qt, Signal, QSize, QDate
from PySide6.QtGui import QAction, QKeySequence, QPainter, QColor, QFont, QCursor
from PySide6.QtWidgets import *

from .constants import PRIORITIES, PRIORITY_LIGHTS, STATUS, THEME_COLORS, EDITOR_PRIORITY_LABELS
from .db import connect, task, tasks, save, remove, subs, backup_db, latest_backup, restore_backup, update_status, update_priority, update_due
from .dialogs import TaskDialog, ProjectDialog


STYLE = f"""
* {{ font-family: 'Segoe UI'; font-size: 10pt; color: {THEME_COLORS['text']}; }}
QMainWindow, QWidget {{ background: {THEME_COLORS['background']}; }}
#topbar {{ background: #ffffff; border-bottom: 1px solid #d8e0e6; }}
#brand {{ font-size: 18pt; font-weight: 700; color: #172b3a; }}
#version {{ background: #f4f6f8; border: 1px solid #d7dee3; border-radius: 6px; padding: 3px 8px; color: #566772; }}
#sidebar {{ background: #034A70; border-right: 1px solid #0B5C82; }}
#sideTitle {{ color: #ffffff; font-size: 8.5pt; font-weight: 700; letter-spacing: .8px; }}
#sideSearch {{ background: #083C57; color: #ffffff; border: 1px solid #38657b; border-radius: 7px; padding: 9px 11px; selection-background-color: #0A82C8; }}
#sideSearch::placeholder {{ color: #bfd2dc; }}
QPushButton#nav {{ border: 0; border-radius: 7px; color: #ffffff; background: transparent; text-align: left; padding: 9px 12px; font-weight: 600; font-size: 10.5pt; min-height: 42px; max-height: 44px; }}
QPushButton#nav:hover {{ background-color: #075C84; color: #ffffff; }}
QPushButton#nav:pressed {{ background-color: #0A6A95; color: #ffffff; }}
QPushButton#nav:disabled {{ background-color: transparent; color: #ffffff; opacity: 1; }}
QPushButton#nav[active='true'] {{ background-color: #087CC1; color: #ffffff; }}
QPushButton#nav[active='true']:hover {{ background-color: #0B86CF; color: #ffffff; }}
QPushButton#nav[active='true']:disabled {{ background-color: #087CC1; color: #ffffff; }}
QPushButton#sideAction {{ border: 1px solid #4B7287; border-radius: 7px; color: #ffffff; background-color: #2A5B72; padding: 9px 12px; text-align: left; font-weight: 600; min-height: 40px; }}
QPushButton#sideAction:hover {{ background-color: #356A82; }}
QPushButton#sideAction:pressed {{ background-color: #214C62; }}
QListWidget#themes {{ background-color: transparent; border: 0; outline: none; padding: 1px 0; }}
QListWidget#themes::item {{ color: #ffffff; background-color: transparent; padding: 8px 10px; border-radius: 7px; margin: 1px 0; min-height: 22px; font-size: 10pt; }}
QListWidget#themes::item:hover {{ background-color: #075C84; color: #ffffff; }}
QListWidget#themes::item:selected {{ background-color: #087CC1; color: #ffffff; font-weight: 700; }}
#overview {{ background-color: #06415F; border: 1px solid #2E647D; border-radius: 8px; }}
#overviewTitle {{ color: #ffffff; font-weight: 700; font-size: 8.5pt; letter-spacing: .5px; }}
#overviewItem {{ color: #ffffff; background: transparent; font-weight: 600; padding: 2px 0; }}
#overviewCount {{ background: #087CC1; color: #ffffff; border-radius: 10px; padding: 1px 7px; font-weight: 700; min-width: 12px; }}
QPushButton#primary {{ background: #0050A4; color: #ffffff; border: 0; border-radius: 7px; padding: 10px 17px; font-weight: 700; }}
QPushButton#primary:hover {{ background: #0068C9; }}
QPushButton#primary:pressed {{ background: #00458F; }}
QLineEdit,QComboBox,QDateEdit,QTextEdit {{ background: #ffffff; border: 1px solid #d5dfe5; border-radius: 7px; padding: 8px; }}
QLineEdit:focus,QComboBox:focus,QDateEdit:focus,QTextEdit:focus {{ border: 1px solid #0074BD; }}
QComboBox::drop-down {{ border: 0; width: 26px; }}
.card {{ background: #ffffff; border: 1px solid #dce4e9; border-radius: 9px; }}
.sectionLabel {{ color: #607582; font-size: 8.5pt; font-weight: 700; letter-spacing: .5px; }}
QTableWidget {{ background: #ffffff; border: 0; gridline-color: #edf1f3; outline: none; }}
QTableWidget::item {{ padding: 7px 8px; border-bottom: 1px solid #eef2f4; }}
QTableWidget::item:selected {{ background: #edf5fb; color: #172b3a; }}
QHeaderView::section {{ background: #ffffff; border: 0; border-bottom: 1px solid #dce4e9; padding: 10px 8px; color: #647580; font-weight: 600; }}
QPushButton#tab {{ border: 0; background: transparent; padding: 9px 12px; color: #253744; font-weight: 600; }}
QPushButton#tab:hover {{ color: #0050A4; }}
QPushButton#tab[active='true'] {{ color: #0050A4; border-bottom: 2px solid #0050A4; }}
QPushButton#soft {{ background: #f5f7f9; border: 1px solid #d8e1e7; border-radius: 7px; padding: 9px 12px; }}
QPushButton#soft:hover {{ background: #eaf2f7; }}
QScrollBar:vertical {{ width: 10px; background: transparent; }}
QScrollBar::handle:vertical {{ background: #4d7890; border-radius: 5px; min-height: 30px; }}
QScrollArea#sidebarScroll {{ background: transparent; border: 0; }}
QScrollArea#sidebarScroll QWidget#sidebarContent {{ background: transparent; }}
QCheckBox {{ spacing: 6px; }}
QCheckBox::indicator {{ width: 15px; height: 15px; }}
QToolTip {{ background: #172b3a; color: #ffffff; border: 0; padding: 5px 7px; }}
"""



class TrafficLight(QWidget):
    def __init__(self, priority=None, parent=None):
        super().__init__(parent)
        self.priority = priority
        self.setMinimumSize(70, 22)
        self.setMaximumSize(84, 28)

    def setPriority(self, priority):
        self.priority = priority
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        colors = PRIORITY_LIGHTS.get(self.priority, ("gray", "gray", "gray"))
        palette = {k: QColor(THEME_COLORS[k]) for k in ("red", "yellow", "green", "gray")}
        radius = 6
        start = 7
        for i, key in enumerate(colors):
            p.setBrush(palette[key])
            p.setPen(Qt.NoPen)
            p.drawEllipse(start + i * 20, 7, radius * 2, radius * 2)
        p.end()


class PriorityCard(QPushButton):
    """Visible, clickable Eisenhower priority selector used by the editor."""
    def __init__(self, priority, parent=None):
        super().__init__(parent)
        self.priority = priority
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(72)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setToolTip(PRIORITIES[priority])

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        border = QColor(THEME_COLORS["primary"] if self.isChecked() else THEME_COLORS["border"])
        fill = QColor(THEME_COLORS["primary_light"] if self.isChecked() else "#FFFFFF")
        p.setBrush(fill); p.setPen(border)
        p.drawRoundedRect(rect, 7, 7)
        keys = PRIORITY_LIGHTS[self.priority]
        palette = {k: QColor(THEME_COLORS[k]) for k in ("red", "yellow", "green", "gray")}
        y = 15
        for i, key in enumerate(keys):
            p.setBrush(palette[key]); p.setPen(Qt.NoPen)
            p.drawEllipse(16 + i * 19, y, 12, 12)
        p.setPen(QColor(THEME_COLORS["text"]))
        f = self.font(); f.setBold(True); f.setPointSize(9); p.setFont(f)
        p.drawText(rect.adjusted(6, 31, -6, -6), Qt.AlignCenter | Qt.TextWordWrap, EDITOR_PRIORITY_LABELS[self.priority])
        p.end()


class ThemeBadge(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text or "Ohne Themengebiet", parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"QLabel{{background:{THEME_COLORS['primary_light']};color:{THEME_COLORS['primary']};"
            f"border:1px solid #c5dced;border-radius:8px;padding:5px 9px;font-weight:600;}}"
        )


class StatusBadge(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(status, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(64)
        self.apply(status)

    def apply(self, status):
        self.setText(status)
        if status == "Erledigt":
            bg, fg, bd = "#e9f7ef", "#16834a", "#cbe9d7"
        elif status == "In Arbeit":
            bg, fg, bd = "#e9f3fb", "#1268a8", "#c7dff2"
        else:
            bg, fg, bd = "#f4f6f7", "#5d6c75", "#d9e0e4"
        self.setStyleSheet(f"QLabel{{background:{bg};color:{fg};border:1px solid {bd};border-radius:7px;padding:5px 8px;font-weight:600;}}")


class DropList(QListWidget):
    moved = Signal(int, str)

    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.drag_id = None
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDrop)

    def startDrag(self, supported):
        if self.currentItem():
            self.drag_id = self.currentItem().data(Qt.UserRole)
        super().startDrag(supported)

    def dropEvent(self, event):
        super().dropEvent(event)
        if self.drag_id is not None:
            self.moved.emit(self.drag_id, self.mode)
        self.drag_id = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arturs Taskmanager V6.2")
        self.resize(1540, 940)
        self.setMinimumSize(1180, 760)
        self.project_filter = None
        self.selected_task = None
        self._undo_available = False
        self.build()
        self.refresh_all()
        self.set_view("tasks")

    def build(self):
        root = QWidget(); self.setCentralWidget(root)
        outer = QVBoxLayout(root); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        top = QFrame(); top.setObjectName("topbar"); top.setFixedHeight(80)
        tl = QHBoxLayout(top); tl.setContentsMargins(26, 14, 22, 14); tl.setSpacing(12)
        brand = QLabel("Arturs Taskmanager"); brand.setObjectName("brand")
        version = QLabel("V6.2"); version.setObjectName("version")
        tl.addWidget(brand); tl.addWidget(version); tl.addStretch()
        self.global_search = QLineEdit(); self.global_search.setPlaceholderText("Suche (Strg + F)"); self.global_search.setMaximumWidth(335); self.global_search.textChanged.connect(self._sync_global_search); tl.addWidget(self.global_search)
        new = QPushButton("＋  Neue Aufgabe (Strg + N)"); new.setObjectName("primary"); new.clicked.connect(self.new_task); tl.addWidget(new)
        self.undo_button = QPushButton("↶  Rückgängig"); self.undo_button.setObjectName("soft"); self.undo_button.setEnabled(bool(latest_backup())); self.undo_button.clicked.connect(self.undo_last); tl.addWidget(self.undo_button)
        settings = QPushButton("⚙  Einstellungen"); settings.setObjectName("soft"); settings.clicked.connect(lambda: QMessageBox.information(self, "Einstellungen", "Arturs Taskmanager arbeitet vollständig offline mit der lokalen Datenbank.")); tl.addWidget(settings)
        minimize = QPushButton("—"); minimize.setObjectName("soft"); minimize.setFixedWidth(36); minimize.clicked.connect(self.showMinimized); tl.addWidget(minimize)
        maximize = QPushButton("□"); maximize.setObjectName("soft"); maximize.setFixedWidth(36); maximize.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized()); tl.addWidget(maximize)
        close = QPushButton("×"); close.setObjectName("soft"); close.setFixedWidth(36); close.clicked.connect(self.close); tl.addWidget(close)
        outer.addWidget(top)

        body = QWidget(); outer.addWidget(body,1); bl = QHBoxLayout(body); bl.setContentsMargins(0,0,0,0); bl.setSpacing(0)
        side = QFrame(); side.setObjectName("sidebar"); side.setFixedWidth(238)
        sl = QVBoxLayout(side); sl.setContentsMargins(12,18,12,14); sl.setSpacing(6)
        self.nav=[]
        nav_items=[("☷   Aufgaben","tasks"),("▥   Kanban","kanban"),("▦   Eisenhower","eisenhower"),("▣   Planung","planning")]
        for label,key in nav_items:
            b=QPushButton(label); b.setObjectName("nav"); b.setCheckable(True); b.setEnabled(True); b.clicked.connect(lambda _,k=key:self.set_view(k)); sl.addWidget(b); self.nav.append((key,b))
        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setStyleSheet("QFrame{color:#2C6680; max-height:1px;}"); sl.addWidget(sep); sl.addSpacing(4)
        for label,key in [("▱   Themengebiete","themes_nav"),("▧   Berichte & Export","reports"),("⚙   Einstellungen","settings_nav"),("?   Hilfe & Info","help")]:
            b=QPushButton(label); b.setObjectName("nav"); b.setEnabled(True)
            if key=="themes_nav": b.clicked.connect(lambda: self.projects.setFocus())
            elif key=="reports": b.clicked.connect(self.export_excel)
            elif key=="settings_nav": b.clicked.connect(lambda: QMessageBox.information(self,"Einstellungen","Lokale Datenbank · Offline-Betrieb · Excel-Export"))
            else: b.clicked.connect(lambda: QMessageBox.information(self,"Hilfe & Info","Aufgabe auswählen, über die Ampel priorisieren und per Kanban verschieben."))
            sl.addWidget(b)
        sl.addSpacing(8)

        # The theme area is independently scrollable so a growing list never
        # squeezes or clips the fixed navigation and overview sections.
        theme_scroll=QScrollArea(); theme_scroll.setObjectName("sidebarScroll"); theme_scroll.setWidgetResizable(True); theme_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); theme_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        theme_content=QWidget(); theme_content.setObjectName("sidebarContent"); tlayout=QVBoxLayout(theme_content); tlayout.setContentsMargins(0,0,0,0); tlayout.setSpacing(6)
        side_title=QLabel("THEMENGEBIETE"); side_title.setObjectName("sideTitle"); side_title.setMinimumHeight(22); tlayout.addWidget(side_title)
        self.project_search=QLineEdit(); self.project_search.setObjectName("sideSearch"); self.project_search.setPlaceholderText("Themengebiete filtern …"); self.project_search.textChanged.connect(self.refresh_projects); tlayout.addWidget(self.project_search)
        self.projects=QListWidget(); self.projects.setObjectName("themes"); self.projects.setMinimumHeight(180); self.projects.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding); self.projects.itemClicked.connect(lambda i:self.set_project(i.data(Qt.UserRole))); self.projects.setContextMenuPolicy(Qt.CustomContextMenu); self.projects.customContextMenuRequested.connect(self.project_menu); tlayout.addWidget(self.projects,1)
        b=QPushButton("＋  Neues Themengebiet"); b.setObjectName("sideAction"); b.clicked.connect(self.new_project); tlayout.addWidget(b)
        theme_scroll.setWidget(theme_content); sl.addWidget(theme_scroll,1)

        overview=QFrame(); overview.setObjectName("overview"); ol=QVBoxLayout(overview); ol.setContentsMargins(12,10,12,10); ot=QLabel("ÜBERSICHT"); ot.setObjectName("overviewTitle"); ol.addWidget(ot)
        self.overview_labels={}
        for key,label in [("Heute","Heute"),("Diese Woche","Diese Woche"),("Später","Später"),("Erledigt","Erledigt"),("Alle","Alle Aufgaben")]:
            row=QHBoxLayout(); lab=QLabel(label); lab.setObjectName("overviewItem"); cnt=QLabel("0"); cnt.setProperty("class","overviewCount"); cnt.setStyleSheet("background:#0078c9; color:white; border-radius:10px; padding:1px 7px; font-weight:700;"); row.addWidget(lab); row.addStretch(); row.addWidget(cnt); ol.addLayout(row); self.overview_labels[key]=cnt
        sl.addWidget(overview)
        offline=QLabel("●  Datenbank verbunden   ·   lokal · offline"); offline.setStyleSheet("color:#cfe1eb;padding:7px 4px;font-size:8.5pt;"); sl.addWidget(offline)
        bl.addWidget(side)

        main=QWidget(); ml=QVBoxLayout(main); ml.setContentsMargins(28,22,26,18); ml.setSpacing(14)
        head=QHBoxLayout(); htext=QVBoxLayout(); self.title_label=QLabel("Aufgaben"); self.title_label.setStyleSheet("font-size:22pt;font-weight:700;color:#172b3a;"); htext.addWidget(self.title_label); sub=QLabel("Ihre Aufgaben im Überblick – nach Priorität und Fälligkeit sortiert"); sub.setStyleSheet("color:#687985;"); htext.addWidget(sub); head.addLayout(htext); head.addStretch(); ml.addLayout(head)
        self.scope_row=QHBoxLayout(); self.scope_buttons={}
        for key,text in [("Heute","Heute"),("Diese Woche","Diese Woche"),("Später","Später"),("Alle","Alle")]:
            b=QPushButton(text); b.setObjectName("tab"); b.setProperty("active","false"); b.clicked.connect(lambda _,k=key:self.set_scope(k)); self.scope_row.addWidget(b); self.scope_buttons[key]=b
        self.scope_row.addStretch(); self.theme_filter=QComboBox(); self.theme_filter.setMinimumWidth(190); self.theme_filter.addItem("Alle Themengebiete",None); self.theme_filter.currentIndexChanged.connect(self._theme_filter_changed); self.scope_row.addWidget(self.theme_filter)
        sort=QPushButton("↕  Sortierung"); sort.setObjectName("soft"); sort.clicked.connect(self.cycle_sort); self.sort_mode=0; self.scope_row.addWidget(sort); ml.addLayout(self.scope_row)
        bar=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Aufgaben suchen …"); self.search.textChanged.connect(self.refresh_all); bar.addWidget(self.search,1); self.pfilter=QComboBox(); self.pfilter.addItem("Alle Prioritäten",None); [self.pfilter.addItem(v,k) for k,v in PRIORITIES.items()]; self.pfilter.currentIndexChanged.connect(self.refresh_all); bar.addWidget(self.pfilter); self.sfilter=QComboBox(); self.sfilter.addItems(["Alle Status"]+STATUS); self.sfilter.currentIndexChanged.connect(self.refresh_all); bar.addWidget(self.sfilter); self.dfilter=QComboBox(); self.dfilter.addItems(["Alle Fälligkeiten","Heute","Diese Woche","Später","Ohne Fälligkeit"]); self.dfilter.currentIndexChanged.connect(self.refresh_all); bar.addWidget(self.dfilter); ml.addLayout(bar)
        self.stack=QStackedWidget(); ml.addWidget(self.stack,1); self.tasks_page=self.task_page(); self.kanban=self.kanban_page(); self.eisen=self.eisen_page(); self.plan=self.plan_page(); [self.stack.addWidget(p) for p in [self.tasks_page,self.kanban,self.eisen,self.plan]]; bl.addWidget(main,1)
        self.shortcut("Ctrl+N",self.new_task); self.shortcut("Ctrl+F",lambda:self.search.setFocus()); self.shortcut("Delete",self.delete_selected); self.scope="Alle"

    def shortcut(self, key, fn):
        a = QAction(self); a.setShortcut(QKeySequence(key)); a.triggered.connect(fn); self.addAction(a)

    def task_page(self):
        p = QWidget(); l = QHBoxLayout(p); l.setContentsMargins(0, 0, 0, 0)
        sp = QSplitter(Qt.Horizontal)
        left = QFrame(); left.setObjectName("card"); ll = QVBoxLayout(left); ll.setContentsMargins(12, 12, 12, 12)
        h = QHBoxLayout(); section = QLabel("AUFGABEN"); section.setObjectName("sectionLabel"); h.addWidget(section); h.addStretch(); self.count = QLabel(); h.addWidget(self.count); ll.addLayout(h)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["", "Aufgabe", "Themengebiet", "Priorität", "Fälligkeit", "Status", ""])
        self.table.setColumnWidth(0, 38); self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for c in [2, 3, 4, 5, 6]: self.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows); self.table.setEditTriggers(QAbstractItemView.NoEditTriggers); self.table.setAlternatingRowColors(False)
        self.table.itemSelectionChanged.connect(self.table_selected); self.table.cellDoubleClicked.connect(lambda r, c: self.edit_selected())
        self.table.setContextMenuPolicy(Qt.CustomContextMenu); self.table.customContextMenuRequested.connect(self.task_menu)
        ll.addWidget(self.table); sp.addWidget(left)
        self.editor = self.editor_panel(); self.editor.setMinimumWidth(390); self.editor.setMaximumWidth(500); sp.addWidget(self.editor); sp.setStretchFactor(0, 1); sp.setStretchFactor(1, 0); sp.setSizes([900, 430]); l.addWidget(sp); return p

    def editor_panel(self):
        right = QFrame(); right.setObjectName("card"); rl = QVBoxLayout(right); rl.setContentsMargins(18, 16, 18, 16)
        editor_label = QLabel("AUFGABE BEARBEITEN"); editor_label.setObjectName("sectionLabel"); rl.addWidget(editor_label)
        self.e_title = QLineEdit(); self.e_title.setPlaceholderText("Aufgabentitel")
        rl.addWidget(QLabel("Titel")); rl.addWidget(self.e_title)
        rl.addWidget(QLabel("Themengebiet")); self.e_project = QComboBox(); rl.addWidget(self.e_project)
        rl.addWidget(QLabel("Priorität (Ampellogik)")); self.priority_buttons = QButtonGroup(self); self.priority_buttons.setExclusive(True); grid = QHBoxLayout(); grid.setSpacing(7)
        self.priority_cards = {}
        for key in PRIORITIES:
            b = PriorityCard(key); b.setMinimumWidth(0); b.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed); b.clicked.connect(lambda _, k=key: self._editor_priority(k)); self.priority_buttons.addButton(b); self.priority_cards[key] = b
            grid.addWidget(b)
        for idx in range(4): grid.setStretch(idx, 1)
        grid.setContentsMargins(0, 0, 0, 0)
        rl.addLayout(grid)
        rl.addWidget(QLabel("Fälligkeit")); due_row = QHBoxLayout(); due_row.setSpacing(8); self.e_due = QDateEdit(); self.e_due.setMinimumWidth(130); self.e_due.setCalendarPopup(True); self.e_due.setDisplayFormat("dd.MM.yyyy"); due_row.addWidget(self.e_due, 1); self.e_no_due = QCheckBox("Keine Fälligkeit"); self.e_no_due.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed); self.e_no_due.toggled.connect(self.e_due.setDisabled); due_row.addWidget(self.e_no_due); due_row.setStretch(0, 1); due_row.setStretch(1, 0); rl.addLayout(due_row)
        rl.addWidget(QLabel("Status")); self.e_status = QComboBox(); self.e_status.addItems(STATUS); rl.addWidget(self.e_status)
        rl.addWidget(QLabel("Beschreibung")); self.e_desc = QTextEdit(); self.e_desc.setMinimumHeight(92); rl.addWidget(self.e_desc)
        sub_head = QHBoxLayout(); sub_head.addWidget(QLabel("Unteraufgaben")); self.sub_count = QLabel(); sub_head.addStretch(); sub_head.addWidget(self.sub_count); rl.addLayout(sub_head)
        self.e_subs = QListWidget(); self.e_subs.setMinimumHeight(115); self.e_subs.setSelectionMode(QAbstractItemView.SingleSelection); self.e_subs.itemChanged.connect(self.update_sub_count); self.e_subs.itemDoubleClicked.connect(self.edit_editor_sub); rl.addWidget(self.e_subs, 1)
        sub_buttons = QHBoxLayout(); add = QPushButton("＋ Unteraufgabe hinzufügen"); add.setObjectName("soft"); add.clicked.connect(self.add_editor_sub); sub_buttons.addWidget(add); edit = QPushButton("Bearbeiten"); edit.setObjectName("soft"); edit.clicked.connect(self.edit_editor_sub); sub_buttons.addWidget(edit); rem = QPushButton("Löschen"); rem.setObjectName("soft"); rem.clicked.connect(self.remove_editor_sub); sub_buttons.addWidget(rem); rl.addLayout(sub_buttons)
        actions = QHBoxLayout(); save_b = QPushButton("Speichern"); save_b.setObjectName("primary"); save_b.clicked.connect(self.save_editor); cancel = QPushButton("Abbrechen"); cancel.setObjectName("soft"); cancel.clicked.connect(lambda: self.select_task(self.selected_task) if self.selected_task else None); actions.addWidget(save_b); actions.addWidget(cancel); rl.addLayout(actions)
        self.editor_task_id = None
        self.editor_project_ids = []
        return right

    def _editor_priority(self, key):
        for k, b in self.priority_cards.items(): b.setChecked(k == key)
        self.editor_priority = key

    def populate_editor(self, r):
        self.editor_task_id = r["id"]
        self.e_title.setText(r["title"])
        self.e_project.clear(); self.e_project.addItem("Kein Themengebiet", None)
        c = connect(); rows = c.execute("SELECT id,name FROM projects ORDER BY name").fetchall(); c.close()
        for x in rows: self.e_project.addItem(x["name"], x["id"])
        i = self.e_project.findData(r["project_id"]); self.e_project.setCurrentIndex(max(0, i))
        self._editor_priority(r["priority"])
        if r["due_date"]:
            self.e_no_due.setChecked(False); self.e_due.setDate(QDate.fromString(r["due_date"], "yyyy-MM-dd"))
        else:
            self.e_no_due.setChecked(True); self.e_due.setDate(QDate.currentDate())
        self.e_status.setCurrentText(r["status"]); self.e_desc.setPlainText(r["description"] or "")
        self.e_subs.blockSignals(True); self.e_subs.clear(); ss = subs(r["id"])
        for s in ss:
            it = QListWidgetItem(s["title"]); it.setFlags(it.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled); it.setCheckState(Qt.Checked if s["done"] else Qt.Unchecked); self.e_subs.addItem(it)
        self.e_subs.blockSignals(False); self.update_sub_count()

    def save_editor(self):
        if not self.editor_task_id or not self.e_title.text().strip():
            QMessageBox.warning(self, "Aufgabe", "Bitte einen Aufgabentitel eingeben.")
            return
        data = {
            "title": self.e_title.text().strip(),
            "project_id": self.e_project.currentData(),
            "priority": getattr(self, "editor_priority", "important_not_urgent"),
            "due_date": None if self.e_no_due.isChecked() else self.e_due.date().toString("yyyy-MM-dd"),
            "status": self.e_status.currentText(),
            "recurrence": task(self.editor_task_id)["recurrence"],
            "description": self.e_desc.toPlainText().strip(),
            "subtasks": [(self.e_subs.item(i).text(), self.e_subs.item(i).checkState() == Qt.Checked) for i in range(self.e_subs.count())]
        }
        save(data, self.editor_task_id, make_backup=True)
        self.selected_task = self.editor_task_id
        self.refresh_all()
        self.statusBar().showMessage("Aufgabe gespeichert", 2500)
        if hasattr(self, "undo_button"): self.undo_button.setEnabled(True)

    def update_sub_count(self, *_):
        done = sum(self.e_subs.item(j).checkState() == Qt.Checked for j in range(self.e_subs.count()))
        self.sub_count.setText(f"{done} / {self.e_subs.count()}")

    def add_editor_sub(self):
        t, ok = QInputDialog.getText(self, "Unteraufgabe", "Unteraufgabe:")
        if ok and t.strip():
            it = QListWidgetItem(t.strip()); it.setFlags(it.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled); it.setCheckState(Qt.Unchecked); self.e_subs.addItem(it); self.e_subs.setCurrentItem(it); self.update_sub_count()

    def edit_editor_sub(self, item=None):
        item = item or self.e_subs.currentItem()
        if not item: return
        t, ok = QInputDialog.getText(self, "Unteraufgabe bearbeiten", "Unteraufgabe:", text=item.text())
        if ok and t.strip(): item.setText(t.strip()); self.update_sub_count()

    def remove_editor_sub(self):
        i = self.e_subs.currentRow()
        if i >= 0:
            self.e_subs.takeItem(i)
            self.update_sub_count()


    def _set_undo_available(self):
        self._undo_available = True
        if hasattr(self, "undo_button"):
            self.undo_button.setEnabled(True)

    def undo_last(self):
        if not self._undo_available:
            self.statusBar().showMessage("Keine Rückgängig-Aktion verfügbar", 2500)
            return
        b = latest_backup()
        if not b:
            self._undo_available = False
            self.undo_button.setEnabled(False)
            self.statusBar().showMessage("Keine Rückgängig-Aktion verfügbar", 2500)
            return
        try:
            consumed = b
            restore_backup(consumed)
            # restore_backup creates a temporary safety backup; remove both it and
            # the consumed snapshot so a second click cannot repeat the same undo.
            for candidate in [consumed, *sorted(consumed.parent.glob("*_before_restore.db"), key=lambda p: p.stat().st_mtime, reverse=True)[:1]]:
                try: candidate.unlink()
                except OSError: pass
            self.selected_task = None
            self.refresh_all()
            self._undo_available = False
            self.undo_button.setEnabled(False)
            self.statusBar().showMessage("Letzte Änderung rückgängig gemacht", 2500)
        except Exception as e:
            QMessageBox.warning(self, "Rückgängig", f"Die Wiederherstellung ist fehlgeschlagen.\n\n{e}")

    def make_list(self, mode):
        w = DropList(mode); w.moved.connect(self.drop_moved); w.itemClicked.connect(lambda i: self.select_task(i.data(Qt.UserRole))); w.itemDoubleClicked.connect(lambda i: self.edit_task(i.data(Qt.UserRole))); return w

    def kanban_page(self):
        p = QWidget(); l = QHBoxLayout(p); l.setContentsMargins(0, 0, 0, 0); self.kcols = {}
        for st in STATUS:
            f = QFrame(); f.setObjectName("card"); fl = QVBoxLayout(f); fl.addWidget(QLabel(st)); w = self.make_list(st); fl.addWidget(w, 1); l.addWidget(f); self.kcols[st] = w
        return p

    def eisen_page(self):
        p = QWidget(); g = QGridLayout(p); g.setContentsMargins(0, 0, 0, 0); self.ecols = {}
        for i, (k, n) in enumerate(PRIORITIES.items()):
            f = QFrame(); f.setObjectName("card"); fl = QVBoxLayout(f); head = QHBoxLayout(); head.addWidget(QLabel(n)); light = TrafficLight(k); head.addWidget(light); fl.addLayout(head); w = self.make_list(k); fl.addWidget(w, 1); g.addWidget(f, i // 2, i % 2); self.ecols[k] = w
        return p

    def plan_page(self):
        p = QWidget(); l = QHBoxLayout(p); l.setContentsMargins(0, 0, 0, 0); self.pcols = {}
        for n in ["Heute", "Diese Woche", "Später"]:
            f = QFrame(); f.setObjectName("card"); fl = QVBoxLayout(f); fl.addWidget(QLabel(n)); w = self.make_list(n); fl.addWidget(w, 1); l.addWidget(f); self.pcols[n] = w
        return p

    def set_view(self, key):
        self.stack.setCurrentIndex({"tasks": 0, "kanban": 1, "eisenhower": 2, "planning": 3}[key]); self.title_label.setText({"tasks": "Aufgaben", "kanban": "Kanban", "eisenhower": "Eisenhower-Matrix", "planning": "Planung"}[key])
        for k, b in self.nav:
            active = (k == key)
            b.setProperty("active", str(active).lower()); b.setChecked(active); b.setEnabled(True); b.style().unpolish(b); b.style().polish(b); b.update()

    def set_scope(self, scope):
        self.scope = scope
        mapping = {"Heute": "Heute", "Diese Woche": "Diese Woche", "Später": "Später", "Alle": "Alle Fälligkeiten"}
        self.dfilter.setCurrentText(mapping[scope])
        for k, b in self.scope_buttons.items():
            b.setProperty("active", str(k == scope).lower()); b.style().unpolish(b); b.style().polish(b)
        self.refresh_all()

    def cycle_sort(self):
        self.sort_mode = (self.sort_mode + 1) % 3
        self.refresh_all()

    def _sync_global_search(self, text):
        if text != self.search.text(): self.search.setText(text)

    def _theme_filter_changed(self):
        if hasattr(self, "theme_filter"): self.project_filter = self.theme_filter.currentData(); self.refresh_all()

    def set_project(self, pid):
        self.project_filter = pid
        if hasattr(self, "theme_filter"):
            i = self.theme_filter.findData(pid)
            if i >= 0 and i != self.theme_filter.currentIndex(): self.theme_filter.blockSignals(True); self.theme_filter.setCurrentIndex(i); self.theme_filter.blockSignals(False)
        self.refresh_all()

    def refresh_projects(self):
        if not hasattr(self, "projects"): return
        q = self.project_search.text().strip().lower(); self.projects.clear()
        it = QListWidgetItem("▦  Alle Themengebiete"); it.setData(Qt.UserRole, None); self.projects.addItem(it)
        c = connect(); rows = c.execute("SELECT id,name FROM projects ORDER BY name").fetchall(); c.close()
        for r in rows:
            if not q or q in r["name"].lower():
                it = QListWidgetItem("▦  " + r["name"]); it.setData(Qt.UserRole, r["id"]); self.projects.addItem(it)
        for i in range(self.projects.count()):
            if self.projects.item(i).data(Qt.UserRole) == self.project_filter: self.projects.setCurrentRow(i); break
        self.refresh_theme_filter(rows)

    def refresh_theme_filter(self, rows=None):
        if not hasattr(self, "theme_filter"): return
        if rows is None:
            c = connect(); rows = c.execute("SELECT id,name FROM projects ORDER BY name").fetchall(); c.close()
        current = self.project_filter; self.theme_filter.blockSignals(True); self.theme_filter.clear(); self.theme_filter.addItem("Alle Themengebiete", None)
        for r in rows: self.theme_filter.addItem(r["name"], r["id"])
        i = self.theme_filter.findData(current); self.theme_filter.setCurrentIndex(max(0, i)); self.theme_filter.blockSignals(False)

    def project_menu(self, pos):
        it = self.projects.itemAt(pos)
        if not it: return
        pid = it.data(Qt.UserRole); m = QMenu(self)
        if pid is not None:
            m.addAction("Bearbeiten …", lambda: self.edit_project(pid)); m.addAction("Löschen …", lambda: self.delete_project(pid))
        m.exec(self.projects.mapToGlobal(pos))

    def new_project(self):
        d = ProjectDialog(self)
        if d.exec() == QDialog.Accepted and d.name():
            try:
                backup_db("before_project_create"); c = connect(); r = c.execute("INSERT INTO projects(name) VALUES(?)", (d.name(),)); self.project_filter = r.lastrowid; c.commit(); c.close(); self.refresh_all(); self.undo_button.setEnabled(True)
            except Exception as e: QMessageBox.warning(self, "Themengebiet", str(e))

    def edit_project(self, pid):
        c = connect(); r = c.execute("SELECT name FROM projects WHERE id=?", (pid,)).fetchone(); c.close()
        if not r: return
        d = ProjectDialog(self, r["name"])
        if d.exec() == QDialog.Accepted and d.name():
            try:
                backup_db("before_project_edit"); c = connect(); c.execute("UPDATE projects SET name=? WHERE id=?", (d.name(), pid)); c.commit(); c.close(); self.refresh_all(); self.undo_button.setEnabled(True)
            except Exception as e: QMessageBox.warning(self, "Themengebiet", str(e))

    def delete_project(self, pid):
        c = connect(); r = c.execute("SELECT name FROM projects WHERE id=?", (pid,)).fetchone(); c.close()
        if r and QMessageBox.question(self, "Themengebiet löschen", f"„{r['name']}“ löschen?") == QMessageBox.Yes:
            backup_db("before_project_delete"); c = connect(); c.execute("UPDATE tasks SET project_id=NULL WHERE project_id=?", (pid,)); c.execute("DELETE FROM projects WHERE id=?", (pid,)); c.commit(); c.close(); self.project_filter = None; self.refresh_all(); self.undo_button.setEnabled(True)

    def new_task(self):
        d = TaskDialog(self, default_project=self.project_filter)
        if d.exec() == QDialog.Accepted:
            v = d.values()
            if v["title"]:
                backup_db("before_create")
                self.selected_task = save(v, make_backup=False)
                self.refresh_all(); self._set_undo_available()

    def select_task(self, tid):
        self.selected_task = tid; r = task(tid)
        if r: self.populate_editor(r)

    def table_selected(self):
        x = self.table.selectionModel().selectedRows()
        if x: self.select_task(self.table.item(x[0].row(), 1).data(Qt.UserRole))

    def edit_selected(self):
        if self.selected_task: self.edit_task(self.selected_task)

    def edit_task(self, tid):
        r = task(tid)
        if r:
            d = TaskDialog(self, r)
            if d.exec() == QDialog.Accepted and d.values()["title"]:
                save(d.values(), tid, make_backup=True); self.selected_task = tid; self.refresh_all(); self._set_undo_available()

    def duplicate_selected(self):
        if not self.selected_task: return
        r = task(self.selected_task); v = dict(r); v["title"] = r["title"] + " (Kopie)"; v["subtasks"] = [(x["title"], bool(x["done"])) for x in subs(self.selected_task)]; v.pop("project_name", None); self.selected_task = save(v, make_backup=True); self.refresh_all(); self.undo_button.setEnabled(True)

    def set_status(self, tid, status):
        if not task(tid): return
        update_status(tid, status)
        self.selected_task = tid
        self.refresh_all()
        self._set_undo_available()

    def delete_selected(self):
        if self.selected_task and QMessageBox.question(self, "Aufgabe löschen", "Aufgabe wirklich löschen?") == QMessageBox.Yes:
            remove(self.selected_task); self.selected_task = None; self.refresh_all(); self._set_undo_available()

    def cycle_priority(self, tid):
        r = task(tid); keys = list(PRIORITIES); update_priority(tid, keys[(keys.index(r["priority"]) + 1) % 4]); self.refresh_all(); self.undo_button.setEnabled(True)

    def refresh_tasks(self):
        rows = tasks(self.project_filter, self.search.text(), self.pfilter.currentData(), self.sfilter.currentText(), self.dfilter.currentText())
        if self.sort_mode == 1: rows = sorted(rows, key=lambda r: (r["due_date"] is None, r["due_date"] or ""))
        elif self.sort_mode == 2: rows = sorted(rows, key=lambda r: r["title"].lower())
        self.count.setText(f"{len(rows)} Aufgaben")
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount(); self.table.insertRow(i); self.table.setRowHeight(i, 52)
            cb = QCheckBox(); cb.setChecked(r["status"] == "Erledigt"); cb.setToolTip("Aufgabe als erledigt markieren"); cb.stateChanged.connect(lambda state, tid=r["id"]: self.set_status(tid, "Erledigt" if state == Qt.Checked.value else "Offen")); cell = QWidget(); cl = QHBoxLayout(cell); cl.setContentsMargins(8, 0, 0, 0); cl.addWidget(cb); self.table.setCellWidget(i, 0, cell)
            ss = subs(r["id"]); done = sum(bool(x["done"]) for x in ss)
            it = QTableWidgetItem(f"{r['title']}\nUnteraufgaben: {done} / {len(ss)}" if ss else r["title"]); it.setData(Qt.UserRole, r["id"]); font = it.font(); font.setWeight(QFont.DemiBold); it.setFont(font); self.table.setItem(i, 1, it)
            self.table.setCellWidget(i, 2, ThemeBadge(r["project_name"]))
            pr = QWidget(); pl = QHBoxLayout(pr); pl.setContentsMargins(4, 0, 4, 0); light = TrafficLight(r["priority"]); light.setToolTip(PRIORITIES[r["priority"]]); pl.addWidget(light); pr.mousePressEvent = lambda _e, tid=r["id"]: self.cycle_priority(tid); self.table.setCellWidget(i, 3, pr)
            due = QTableWidgetItem(self.fmt(r["due_date"]));
            if r["due_date"] == date.today().isoformat(): due.setForeground(QColor(THEME_COLORS["red"]));
            self.table.setItem(i, 4, due)
            sb = StatusBadge(r["status"]); sb.mousePressEvent = lambda _e, tid=r["id"]: self.toggle_task(tid); self.table.setCellWidget(i, 5, sb)
            more = QPushButton("•••"); more.setObjectName("soft"); more.setFixedWidth(42); more.clicked.connect(lambda _, tid=r["id"]: self.open_task_actions(tid)); self.table.setCellWidget(i, 6, more)
        if self.selected_task: self.select_task(self.selected_task)

    def open_task_actions(self, tid):
        self.selected_task = tid; m = QMenu(self); m.addAction("Bearbeiten …", lambda: self.edit_task(tid)); m.addAction("Status wechseln", lambda: self.toggle_task(tid)); m.addAction("Priorität wechseln", lambda: self.cycle_priority(tid)); m.addAction("Duplizieren", self.duplicate_selected); m.addAction("Löschen …", self.delete_selected); m.exec(QCursor.pos())

    def toggle_task(self, tid):
        r = task(tid); self.set_status(tid, {"Offen": "In Arbeit", "In Arbeit": "Erledigt", "Erledigt": "Offen"}[r["status"]])

    def refresh_kanban(self):
        for w in self.kcols.values(): w.clear()
        for r in tasks(self.project_filter):
            it = QListWidgetItem(f"{r['title']}\n{PRIORITIES[r['priority']]} · {self.fmt(r['due_date'])}"); it.setData(Qt.UserRole, r["id"]); self.kcols[r["status"]].addItem(it)

    def refresh_eisen(self):
        for w in self.ecols.values(): w.clear()
        for r in tasks(self.project_filter):
            it = QListWidgetItem(f"{r['title']}\n{self.fmt(r['due_date'])}"); it.setData(Qt.UserRole, r["id"]); self.ecols[r["priority"]].addItem(it)

    def refresh_plan(self):
        for w in self.pcols.values(): w.clear()
        today = date.today(); end = today + timedelta(days=6 - today.weekday())
        for r in tasks(self.project_filter):
            if not r["due_date"]: g = "Später"
            else:
                d = datetime.strptime(r["due_date"], "%Y-%m-%d").date(); g = "Heute" if d == today else ("Diese Woche" if d <= end else "Später")
            it = QListWidgetItem(f"{r['title']}\n{PRIORITIES[r['priority']]} · {self.fmt(r['due_date'])}"); it.setData(Qt.UserRole, r["id"]); self.pcols[g].addItem(it)

    def drop_moved(self, tid, target):
        if target in STATUS: self.set_status(tid, target)
        elif target in PRIORITIES:
            update_priority(tid, target); self.refresh_all(); self.undo_button.setEnabled(True)
        else:
            due = date.today().isoformat() if target == "Heute" else ((date.today() + timedelta(days=2)).isoformat() if target == "Diese Woche" else None)
            update_due(tid, due); self.refresh_all(); self.undo_button.setEnabled(True)

    def task_menu(self, pos):
        it = self.table.itemAt(pos)
        if not it: return
        tid = self.table.item(it.row(), 1).data(Qt.UserRole); self.selected_task = tid; m = QMenu(self); m.addAction("Bearbeiten …", lambda: self.edit_task(tid)); m.addAction("Status wechseln", lambda: self.toggle_task(tid)); m.addAction("Priorität wechseln", lambda: self.cycle_priority(tid)); m.addAction("Duplizieren", self.duplicate_selected); m.addAction("Löschen …", self.delete_selected); m.exec(self.table.viewport().mapToGlobal(pos))

    def fmt(self, s):
        if not s: return "—"
        try: return datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception: return s

    def export_excel(self):
        from PySide6.QtWidgets import QFileDialog
        try:
            from openpyxl import Workbook
            path, _ = QFileDialog.getSaveFileName(self, "Aufgaben exportieren", "Arturs_Taskmanager_Aufgaben.xlsx", "Excel-Dateien (*.xlsx)")
            if not path:
                return
            wb = Workbook(); ws = wb.active; ws.title = "Aufgaben"
            ws.append(["Aufgabe", "Themengebiet", "Priorität", "Fälligkeit", "Status", "Beschreibung", "Unteraufgaben"])
            for r in tasks():
                ss = subs(r["id"]); done = sum(bool(x["done"]) for x in ss)
                ws.append([r["title"], r["project_name"] or "", PRIORITIES[r["priority"]], self.fmt(r["due_date"]), r["status"], r["description"] or "", f"{done}/{len(ss)}"])
            wb.save(path)
            QMessageBox.information(self, "Export", "Die Aufgaben wurden erfolgreich exportiert.")
        except Exception as e:
            QMessageBox.warning(self, "Export", f"Der Export konnte nicht erstellt werden.\n\n{e}")

    def refresh_all(self):
        self.refresh_projects(); self.refresh_tasks(); self.refresh_kanban(); self.refresh_eisen(); self.refresh_plan()
        if hasattr(self, "overview_labels"):
            all_rows = tasks()
            today = date.today(); week_end = today + timedelta(days=6-today.weekday())
            counts = {"Heute": 0, "Diese Woche": 0, "Später": 0, "Erledigt": 0, "Alle": len(all_rows)}
            for r in all_rows:
                if r["status"] == "Erledigt": counts["Erledigt"] += 1
                if not r["due_date"]: counts["Später"] += 1
                else:
                    d = datetime.strptime(r["due_date"], "%Y-%m-%d").date()
                    if d == today: counts["Heute"] += 1
                    elif d <= week_end: counts["Diese Woche"] += 1
                    else: counts["Später"] += 1
            for k,v in counts.items():
                self.overview_labels[k].setText(str(v))
