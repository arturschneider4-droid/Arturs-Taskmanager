from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from PySide6.QtWidgets import QHeaderView, QAbstractItemView, QSizePolicy, QCheckBox


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
            widget.setMaximumWidth(max(1, width - 2))
            layout = widget.layout()
            if layout is not None:
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
            widget.updateGeometry()


def _install_task_checkbox_controller(controller):
    """Make the first-column task completion control reliably clickable."""
    table = controller.table
    if table is None:
        return
    for row in range(table.rowCount()):
        cell = table.cellWidget(row, 0)
        if cell is None or getattr(cell, "_task_checkbox_bound", False):
            continue
        checkbox = cell.findChild(QCheckBox)
        if checkbox is None:
            continue
        # The containing cell owns the click. This remains reliable even when
        # responsive sizing makes the embedded checkbox extremely narrow.
        checkbox.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        cell.installEventFilter(controller)
        cell._task_checkbox_bound = True


def _schedule_responsive_refresh(controller):
    QTimer.singleShot(0, lambda: (
        _bound_embedded_task_controls(controller.table),
        _install_task_checkbox_controller(controller),
    ))


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

    controller = getattr(window, "_responsive_task_controller", None)
    if controller is None:
        splitter = left.parentWidget() if left is not None else None
        controller = _TaskAreaController(window, table, splitter)
        window._responsive_task_controller = controller
    _install_task_checkbox_controller(controller)

    model = table.model()
    if model is not None and not getattr(table, "_responsive_rows_hooked", False):
        model.rowsInserted.connect(lambda *_: _schedule_responsive_refresh(controller))
        table._responsive_rows_hooked = True

    splitter = left.parentWidget() if left is not None else None
    if splitter is not None and hasattr(splitter, "setChildrenCollapsible"):
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([TASK_LEFT_MIN_WIDTH, EDITOR_MIN_WIDTH])


class _TaskAreaController(QObject):
    def __init__(self, window, table, splitter):
        super().__init__(window)
        self.window = window
        self.table = table
        self.splitter = splitter
        if table is not None:
            table.installEventFilter(self)
            table.viewport().installEventFilter(self)
        if splitter is not None:
            splitter.installEventFilter(self)

    def _toggle_row(self, row):
        if row < 0:
            return False
        item = self.table.item(row, 1)
        if item is None:
            return False
        tid = item.data(Qt.UserRole)
        if tid is None or not hasattr(self.window, "set_status"):
            return False
        cell = self.table.cellWidget(row, 0)
        checkbox = cell.findChild(QCheckBox) if cell is not None else None
        checked = checkbox.isChecked() if checkbox is not None else False
        self.window.set_status(tid, "Offen" if checked else "Erledigt")
        return True

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if getattr(obj, "_task_checkbox_bound", False):
                pos = self.table.viewport().mapFrom(obj, event.position().toPoint())
                row = self.table.indexAt(pos).row()
                if self._toggle_row(row):
                    return True
            elif obj is self.table.viewport():
                index = self.table.indexAt(event.position().toPoint())
                if index.isValid() and index.column() == 0:
                    if self._toggle_row(index.row()):
                        return True
        if event.type() == QEvent.Resize:
            self.table.horizontalScrollBar().setValue(0)
            _bound_embedded_task_controls(self.table)
            _install_task_checkbox_controller(self)
        return super().eventFilter(obj, event)
