"""Small V7 editor interaction hardening helpers."""

from PySide6.QtWidgets import QPushButton


def configure_editor_subtask_controls(window):
    """Enable subtask edit/delete actions only when a subtask is selected."""
    edit = None
    remove = None
    for button in window.editor.findChildren(QPushButton):
        if button.text() == "Bearbeiten":
            edit = button
        elif button.text() == "Löschen":
            remove = button

    if edit is None or remove is None:
        return False

    if not getattr(window, "_v7_editor_subtask_controls_installed", False):
        window._v7_editor_subtask_controls_installed = True
        window.e_subs.currentItemChanged.connect(
            lambda current, _previous: _update_subtask_actions(current, edit, remove)
        )

    _update_subtask_actions(window.e_subs.currentItem(), edit, remove)
    return True


def _update_subtask_actions(item, edit, remove):
    enabled = item is not None
    edit.setEnabled(enabled)
    remove.setEnabled(enabled)
