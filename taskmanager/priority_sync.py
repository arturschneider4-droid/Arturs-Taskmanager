"""Immediate UI synchronization patches for task priority and editing.

The editor actions persist through the normal SQLite layer, then explicitly
synchronize the visible task table so the desktop view never depends on a
stale selection/model state.
"""

from datetime import date

from .constants import PRIORITIES, THEME_COLORS
from .db import backup_db, task, update_priority
from .ui import MainWindow, TrafficLight
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtGui import QColor, QFont


_original_editor_priority = MainWindow._editor_priority
_original_edit_task = MainWindow.edit_task


def _synced_editor_priority(self, key):
    previous = getattr(self, "editor_priority", None)
    _original_editor_priority(self, key)

    tid = getattr(self, "editor_task_id", None)
    if not tid or previous == key:
        return

    current = task(tid)
    if not current or current["priority"] == key:
        return

    backup_db("before_priority_change")
    update_priority(tid, key)
    self.selected_task = tid

    if hasattr(self, "table"):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item and item.data(Qt.UserRole) == tid:
                cell = QWidget()
                layout = QHBoxLayout(cell)
                layout.setContentsMargins(4, 0, 4, 0)
                light = TrafficLight(key)
                light.setToolTip(PRIORITIES[key])
                layout.addWidget(light)
                cell.mousePressEvent = lambda _event, task_id=tid: self.cycle_priority(task_id)
                self.table.setCellWidget(row, 3, cell)
                break

    if hasattr(self, "kcols"):
        self.refresh_kanban()
    if hasattr(self, "ecols"):
        self.refresh_eisen()
    if hasattr(self, "pcols"):
        self.refresh_plan()

    if hasattr(self, "_set_undo_available"):
        self._set_undo_available()
    elif hasattr(self, "undo_button"):
        self.undo_button.setEnabled(True)
    if hasattr(self, "statusBar"):
        self.statusBar().showMessage("Priorität gespeichert", 1800)


def _sync_due_visuals(self):
    """Color today's and overdue due dates after the normal table rebuild."""
    if not hasattr(self, "table"):
        return
    today = date.today().isoformat()
    for row in range(self.table.rowCount()):
        item = self.table.item(row, 1)
        due_item = self.table.item(row, 4)
        if not item or not due_item:
            continue
        tid = item.data(Qt.UserRole)
        current = task(tid) if tid is not None else None
        due = current["due_date"] if current else None
        if due and due < today:
            due_item.setForeground(QColor(THEME_COLORS["red"]))
        elif due == today:
            due_item.setForeground(QColor(THEME_COLORS["red"]))


def _synced_edit_task(self, tid):
    """Run the existing editor, then force a complete visible task refresh."""
    _original_edit_task(self, tid)
    if not task(tid):
        return
    self.selected_task = tid
    self.refresh_all()
    _sync_due_visuals(self)
    for row in range(self.table.rowCount()):
        item = self.table.item(row, 1)
        if item and item.data(Qt.UserRole) == tid:
            self.table.selectRow(row)
            self.table.scrollToItem(item)
            self.table.viewport().update()
            break


MainWindow._editor_priority = _synced_editor_priority
MainWindow.edit_task = _synced_edit_task


def apply_priority_sync():
    """Compatibility entry point; importing this module applies both patches."""
    return MainWindow._editor_priority
