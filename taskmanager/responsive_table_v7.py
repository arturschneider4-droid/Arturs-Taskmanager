from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QHeaderView, QAbstractItemView


TASK_FIXED_WIDTHS = {0: 30, 2: 90, 3: 85, 4: 85, 5: 70, 6: 40}
TASK_LEFT_MIN_WIDTH = 500
EDITOR_MIN_WIDTH = 300
EDITOR_MAX_WIDTH = 380


def configure_responsive_task_area(window):
    table = getattr(window, "table", None)
    editor = getattr(window, "editor", None)
    if table is None or editor is None:
        return

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
        if column != 0:
            header.setSectionResizeMode(column, QHeaderView.Fixed)
        table.setColumnWidth(column, width)

    table.setWordWrap(False)
    table.setTextElideMode(Qt.ElideRight)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.horizontalScrollBar().setValue(0)

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
        return super().eventFilter(obj, event)
