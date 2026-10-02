from __future__ import annotations

from dataclasses import replace
from datetime import date

from PySide6.QtCore import Qt, Signal, QMimeData, QSize, QTimer
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu, QVBoxLayout, QWidget

from .repositories import QuerySpec
from .task_store import SaveTask, TaskStore


STATUSES = ("Offen", "In Arbeit", "Erledigt")
PRIORITIES = ("important_urgent", "important_not_urgent", "not_important_urgent", "not_important_not_urgent")


PRIORITY_STYLES = {
    "important_urgent": ("Wichtig & dringend", "#A3293D", "#FCECEF"),
    "important_not_urgent": ("Wichtig", "#175A9B", "#EAF2FC"),
    "not_important_urgent": ("Dringend", "#885000", "#FFF3D6"),
    "not_important_not_urgent": ("Später", "#52616D", "#EDF1F4"),
}


class KanbanCard(QFrame):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        label, color, background = PRIORITY_STYLES[task.priority]
        self.setObjectName("kanbanCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        # The list handles clicking, keyboard selection and dragging.
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet(f"QFrame#kanbanCard {{ background: white; border: 1px solid #DDE4E9; border-left: 5px solid {color}; border-radius: 7px; }} QLabel {{ border: 0; background: transparent; }}")
        layout = QVBoxLayout(self); layout.setContentsMargins(12, 10, 10, 10); layout.setSpacing(7)
        title = QLabel(("★ " if task.is_top_three else "") + task.title)
        title.setWordWrap(True); title.setTextFormat(Qt.PlainText)
        layout.addWidget(title)
        deadline = "Deadline: " + task.deadline.strftime("%d.%m.%Y") if task.deadline else "Keine Deadline"
        if task.deadline and task.deadline < date.today() and task.status != "Erledigt": deadline += " · überfällig"
        self.deadline_label = QLabel(deadline); self.deadline_label.setWordWrap(True)
        layout.addWidget(self.deadline_label)
        badge = QLabel(label); badge.setObjectName("kanban_priority"); badge.setWordWrap(True)
        badge.setStyleSheet(f"color: {color}; background: {background}; border-radius: 4px; padding: 4px 6px; font-weight: 600;")
        layout.addWidget(badge)
        self.setAccessibleName(f"{task.title}. {deadline}. {label}")


class BoardLane(QListWidget):
    MIME = "application/x-arturs-task-id"

    def __init__(self, board, lane):
        super().__init__(board)
        self.board, self.lane = board, lane
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setWordWrap(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSpacing(8)
        self.setObjectName("boardLane")
        if board.field == "status":
            self.setStyleSheet("QListWidget#boardLane::item { padding: 0px; border: 0px; background: transparent; }")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu)
        self.itemClicked.connect(lambda item: board.task_selected.emit(item.data(Qt.UserRole)))
        self.itemActivated.connect(lambda item: board.task_selected.emit(item.data(Qt.UserRole)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._size_cards)

    def _size_cards(self):
        for index in range(self.count()):
            item = self.item(index); card = self.itemWidget(item)
            if card is not None:
                width = max(50, self.visualItemRect(item).width())
                height = max(132, card.layout().totalHeightForWidth(width - 6) + 4)
                size = QSize(width, height)
                if item.sizeHint() != size: item.setSizeHint(size)

    def startDrag(self, actions):
        item = self.currentItem()
        if item is None: return
        mime = QMimeData(); mime.setData(self.MIME, str(item.data(Qt.UserRole)).encode())
        drag = QDrag(self); drag.setMimeData(mime); drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(self.MIME): event.acceptProposedAction()
        else: event.ignore()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        try:
            task_id = int(bytes(event.mimeData().data(self.MIME)))
        except (ValueError, TypeError):
            event.ignore(); return
        if self.board.move_task(task_id, self.lane): event.acceptProposedAction()
        else: event.ignore()

    def _menu(self, pos):
        item = self.itemAt(pos)
        if item is None: return
        task_id = item.data(Qt.UserRole)
        menu = QMenu(self)
        menu.addAction("Details öffnen", lambda: self.board.task_selected.emit(task_id))
        for lane in self.board.lanes:
            menu.addAction(self.board.label_for(lane), lambda _=False, target=lane: self.board.move_task(task_id, target))
        menu.exec(self.viewport().mapToGlobal(pos))


class BoardView(QWidget):
    task_selected = Signal(int)
    lanes: tuple[str, ...] = ()
    field = ""

    def __init__(self, store: TaskStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.query = QuerySpec()
        self._summaries = []
        root = QVBoxLayout(self)
        lane_row = QGridLayout()
        columns = 2 if self.field == "priority" else 3
        self.lane_widgets = {}
        self.lane_labels = {}
        for index, lane in enumerate(self.lanes):
            column = QWidget(); layout = QVBoxLayout(column)
            label = QLabel(self.label_for(lane)); label.setObjectName("laneTitle")
            self.lane_labels[lane] = label; layout.addWidget(label)
            listing = BoardLane(self, lane); layout.addWidget(listing)
            self.lane_widgets[lane] = listing; lane_row.addWidget(column, index // columns, index % columns)
        root.addLayout(lane_row)
        self.store.changed.connect(lambda change: self.refresh() if "tasks" in change.domains else None)
        self.refresh()

    def label_for(self, lane):
        return lane

    def set_query(self, spec: QuerySpec):
        self.query = spec; self.refresh()

    def titles(self):
        return [item.title for item in self._summaries]

    def refresh(self):
        self._summaries = self.store.repository.query(self.query)
        for listing in self.lane_widgets.values(): listing.clear()
        for item in self._summaries:
            lane = getattr(item, self.field)
            if lane == "Ohne Termin" and self.field == "status": lane = "Offen"
            if lane in self.lane_widgets:
                card = QListWidgetItem(("★ " if item.is_top_three else "") + item.title)
                card.setData(Qt.UserRole, item.id)
                card.setToolTip(f"{item.title}\n{item.status} · {item.project_name or 'Ohne Themengebiet'}\nZiehen zum Verschieben · Rechtsklick für Aktionen")
                card.setSizeHint(QSize(120, 76))
                listing = self.lane_widgets[lane]
                listing.addItem(card)
                if self.field == "status":
                    widget = KanbanCard(item)
                    card.setToolTip(widget.accessibleName() + "\nZiehen zum Verschieben · Rechtsklick für Aktionen")
                    card.setData(Qt.AccessibleTextRole, widget.accessibleName())
                    listing.setItemWidget(card, widget)
                    QTimer.singleShot(0, listing._size_cards)
        for lane, listing in self.lane_widgets.items():
            self.lane_labels[lane].setText(f"{self.label_for(lane)} · {listing.count()}")

    def move_task(self, task_id: int, lane: str) -> bool:
        if lane not in self.lanes: return False
        record = self.store.repository.get(task_id)
        if record is None: return False
        result = self.store.apply(SaveTask(replace(record.draft, **{self.field: lane}), task_id))
        return result.ok


class KanbanView(BoardView):
    lanes = STATUSES
    field = "status"


class EisenhowerView(BoardView):
    lanes = PRIORITIES
    field = "priority"
    def label_for(self, lane):
        return {
            "important_urgent": "Wichtig & dringend", "important_not_urgent": "Wichtig",
            "not_important_urgent": "Dringend", "not_important_not_urgent": "Später",
        }[lane]
