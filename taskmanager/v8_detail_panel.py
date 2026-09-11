"""V8 task inspector and premium task-surface presentation controller.

The existing V7 editor and task refresh logic remain the functional source of
truth. V8 only adds presentation semantics around that existing hierarchy.
"""

from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtGui import QColor, QFont


class V8DetailPanel(QObject):
    """Own the V8 inspector state while delegating editing to MainWindow."""

    MIN_WIDTH = 320
    MAX_WIDTH = 650
    DEFAULT_WIDTH = 380
    NARROW_BREAKPOINT = 960

    # Semantic row roles used by the V8 premium task surface.
    V8_TASK_ROLES = (
        "v8TaskRow",
        "v8TaskTitle",
        "v8TaskMeta",
        "v8TaskStatus",
        "v8TaskPriority",
        "v8TaskDue",
    )

    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.editor = getattr(window, "editor", None)
        self.splitter = self.editor.parentWidget() if self.editor is not None else None
        self._task_id = getattr(window, "selected_task", None)
        self._panel_width = self.DEFAULT_WIDTH
        self._requested_open = False

        if self.editor is not None:
            self.editor.installEventFilter(self)

        table = getattr(window, "table", None)
        if table is not None:
            table.itemSelectionChanged.connect(self.sync_from_selection)
            self._install_task_surface(table)

    @property
    def task_id(self):
        return self._task_id

    @property
    def panel_open(self):
        return bool(self.editor is not None and self.editor.isVisible())

    @property
    def panel_width(self):
        return self._panel_width

    def set_task_id(self, tid):
        self._task_id = tid
        if tid is None:
            return
        self.window.selected_task = tid
        select_task = getattr(self.window, "select_task", None)
        if callable(select_task):
            select_task(tid)

    def clear_task(self):
        self._task_id = None
        self._requested_open = False
        self.set_panel_open(False)

    def set_panel_open(self, open_):
        self._requested_open = bool(open_)
        if self.editor is None:
            return
        self.editor.setVisible(self._requested_open)
        self._apply_width()

    def set_panel_width(self, width):
        self._panel_width = max(self.MIN_WIDTH, min(self.MAX_WIDTH, int(width)))
        self._apply_width()

    def handle_window_width(self, width):
        """Apply the V8 responsive rule without discarding selection state."""
        if self.editor is None:
            return
        if width < self.NARROW_BREAKPOINT:
            self.editor.setVisible(False)
        else:
            self.editor.setVisible(self._requested_open)
            if self.editor.isVisible() and self._task_id is not None:
                select_task = getattr(self.window, "select_task", None)
                if callable(select_task):
                    select_task(self._task_id)
        self._apply_width()

    def eventFilter(self, watched, event):
        if watched is self.editor and event.type() == QEvent.Hide and self.window.width() >= self.NARROW_BREAKPOINT:
            self._requested_open = False
        elif watched is self.editor and event.type() == QEvent.Show:
            self._requested_open = True
        return super().eventFilter(watched, event)

    def sync_from_selection(self):
        tid = getattr(self.window, "selected_task", None)
        if tid is not None:
            self._task_id = tid
            self._requested_open = True
            self.set_panel_open(True)

    def _apply_width(self):
        if self.splitter is None or not hasattr(self.splitter, "setSizes"):
            return
        total = max(0, self.splitter.width())
        if self.panel_open:
            self.splitter.setSizes([max(450, total - self._panel_width), self._panel_width])
        else:
            self.splitter.setSizes([max(450, total), 0])

    def _install_task_surface(self, table):
        """Apply premium V8 hierarchy while retaining the original table API."""
        table.setObjectName("v8TaskRows")
        table.setAlternatingRowColors(False)
        table.setShowGrid(False)
        table.setWordWrap(False)
        table.setTextElideMode(Qt.ElideRight)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setStyleSheet(
            "QTableWidget#v8TaskRows{background:#FFFFFF;border:0;}"
            "QTableWidget#v8TaskRows::item{padding:7px 8px;border-bottom:1px solid #EEF2F4;}"
            "QTableWidget#v8TaskRows::item:selected{background:#E7F1FA;color:#172B3A;}"
            "QHeaderView::section{background:#FFFFFF;border:0;border-bottom:1px solid #DCE4E9;"
            "padding:8px;color:#74838C;font-size:8pt;font-weight:700;}"
        )

        if not getattr(self.window, "_v8_refresh_tasks_wrapped", False):
            refresh_tasks = getattr(self.window, "refresh_tasks", None)
            if callable(refresh_tasks):
                def refresh_tasks_v8(*args, **kwargs):
                    result = refresh_tasks(*args, **kwargs)
                    self.apply_task_row_hierarchy()
                    return result
                self.window.refresh_tasks = refresh_tasks_v8
                self.window._v8_refresh_tasks_wrapped = True

        self.apply_task_row_hierarchy()

    def apply_task_row_hierarchy(self):
        """Style existing task items after every functional table refresh."""
        table = getattr(self.window, "table", None)
        if table is None:
            return
        for row in range(table.rowCount()):
            title_item = table.item(row, 1)
            if title_item is not None:
                font = QFont(title_item.font())
                font.setBold(True)
                font.setPointSize(max(9, font.pointSize()))
                title_item.setFont(font)
                title_item.setForeground(QColor("#172B3A"))
                title_item.setData(Qt.UserRole + 1, "v8TaskTitle")

            theme_item = table.item(row, 2)
            if theme_item is not None:
                theme_item.setData(Qt.UserRole + 1, "v8TaskMeta")

            due_item = table.item(row, 4)
            if due_item is not None:
                due_item.setData(Qt.UserRole + 1, "v8TaskDue")
                due_item.setForeground(QColor("#C23B3B") if "Heute" in due_item.text() else QColor("#53656F"))

            status_item = table.item(row, 5)
            if status_item is not None:
                status_item.setData(Qt.UserRole + 1, "v8TaskStatus")

            priority_item = table.item(row, 3)
            if priority_item is not None:
                priority_item.setData(Qt.UserRole + 1, "v8TaskPriority")

            check_item = table.item(row, 0)
            if check_item is not None:
                check_item.setData(Qt.UserRole + 1, "v8TaskRow")


def install_v8_detail_panel(window):
    """Install and return the reusable V8 inspector controller."""
    existing = getattr(window, "_v8_detail_panel", None)
    if existing is not None:
        return existing
    panel = V8DetailPanel(window)
    window._v8_detail_panel = panel
    if not getattr(window, "_v8_detail_resize_installed", False):
        original_resize = window.resizeEvent

        def resize_event(event):
            original_resize(event)
            panel.handle_window_width(window.width())

        window.resizeEvent = resize_event
        window._v8_detail_resize_installed = True
    return panel
