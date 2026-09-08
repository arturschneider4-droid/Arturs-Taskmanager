from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from PySide6.QtWidgets import QHeaderView, QAbstractItemView, QSizePolicy


# The table must retain enough room for the title column while every embedded
# control remains inside its own cell. These dimensions are deliberately small
# enough to keep the complete task workspace usable on a reduced window.
TASK_FIXED_WIDTHS = {0: 32, 2: 100, 3: 95, 4: 100, 5: 85, 6: 50}
TASK_LEFT_MIN_WIDTH = 600
EDITOR_MIN_WIDTH = 300
EDITOR_MAX_WIDTH = 400
TASK_WINDOW_MIN_WIDTH = 1200


def _bound_embedded_task_controls(table):
    """Keep every cell widget inside its column without horizontal overflow."""
    for column, width in TASK_FIXED_WIDTHS.items():
        for row in range(table.rowCount()):
            widget = table.cellWidget(row, column)
            if widget is None:
                continue
            widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            widget.setMinimumWidth(0)
            widget.setMaximumWidth(max(1, width - 6))
            layout = widget.layout()
            if layout is not None:
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
            widget.updateGeometry()


def _schedule_cell_bounds(table):
    QTimer.singleShot(0, lambda: _bound_embedded_task_controls(table))


def configure_responsive_task_area(window):
    table = getattr(window, "table", None)
    editor = getattr(window, "editor", None)
    if table is None or editor is None:
        return

    window.setMinimumSize(TASK_WINDOW_MIN_WIDTH, 760)

    left = table.parentWidget()
    if left is not None:
        left.setMinimumWidth(TASK_LEFT_MIN_WIDTH)

    editor.setMinimumWidth(EDITOR_MIN_WIDTH)
    editor.setMaximumWidth(EDITOR_MAX_WIDTH)

    header = table.horizontalHeader()
    header.setStretchLastSection(False)
    header.setMinimumSectionSize(30)
    header.setSectionResizeMode(0, QHeaderView.Fixed)
    header.setSectionResizeMode(1, QHeaderView.Stretch)
    for column, width in TASK_FIXED_WIDTHS.items():
        header.setSectionResizeMode(column, QHeaderView.Fixed)
        table.setColumnWidth(column, width)

    table.setWordWrap(False)
    table.setTextElideMode(Qt.ElideRight)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.horizontalScrollBar().setValue(0)
    _bound_embedded_task_controls(table)

    model = table.model()
    if model is not None and not getattr(table, "_responsive_rows_hooked", False):
        model.rowsInserted.connect(lambda *_: _schedule_cell_bounds(table))
        table._responsive_rows_hooked = True

    splitter = left.parentWidget() if left is not None else None
    if splitter is not None and hasattr(splitter, "setChildrenCollapsible"):
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([TASK_LEFT_MIN_WIDTH, EDITOR_MIN_WIDTH])

    controller = getattr(window, "_responsive_task_controller", None)
    if controller is None:
        controller = _TaskAreaController(window, table, splitter)
        window._responsive_task_controller = controller


class _TaskAreaController(QObject):
    def __init__(self, window, table, splitter):
        super().__init__(window)
        self.table = table
        self.splitter = splitter
        if table is not None:
            table.installEventFilter(self)
            table.viewport().installEventFilter(self)
        if splitter is not None:
            splitter.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.table.horizontalScrollBar().setValue(0)
            _bound_embedded_task_controls(self.table)
        return super().eventFilter(obj, event)
