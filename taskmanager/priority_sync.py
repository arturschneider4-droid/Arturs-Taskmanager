"""V6.2.1 priority synchronization patch.

The editor's Eisenhower priority cards are immediate actions.  This module
keeps that action separate from the normal Save operation so unsaved title,
description, due date, status, and subtasks are not lost when priority changes.
"""

from .constants import PRIORITIES
from .db import backup_db, task, update_priority
from .ui import MainWindow, TrafficLight, ThemeBadge, StatusBadge
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget, QTableWidgetItem, QFont
from PySide6.QtGui import QColor


_original_editor_priority = MainWindow._editor_priority


def _synced_editor_priority(self, key):
    previous = getattr(self, "editor_priority", None)
    _original_editor_priority(self, key)

    tid = getattr(self, "editor_task_id", None)
    if not tid or previous == key:
        return

    current = task(tid)
    if not current or current["priority"] == key:
        return

    # Priority is an explicit immediate action, so persist it independently of
    # the other editor fields, which may still contain unsaved changes.
    backup_db("before_priority_change")
    update_priority(tid, key)
    self.selected_task = tid

    # Update the visible task-list priority cell without reloading the editor.
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

    # Other views derive their priority from SQLite and can therefore be
    # refreshed safely without touching the editor fields.
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


MainWindow._editor_priority = _synced_editor_priority


def apply_priority_sync():
    """Compatibility entry point; importing this module applies the patch."""
    return MainWindow._editor_priority
