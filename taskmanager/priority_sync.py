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
    # Editor choices are drafts until the user presses Save.
    _original_editor_priority(self, key)


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
