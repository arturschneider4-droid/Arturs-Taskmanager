"""V8 task inspector state controller.

The existing V7 editor remains the functional source of truth. This small
controller gives the V8 presentation a stable inspector contract without
moving or duplicating task-editing widgets.
"""

from PySide6.QtCore import QObject, QEvent


class V8DetailPanel(QObject):
    """Own the V8 inspector state while delegating editing to MainWindow."""

    MIN_WIDTH = 320
    MAX_WIDTH = 650
    DEFAULT_WIDTH = 380
    NARROW_BREAKPOINT = 960

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
