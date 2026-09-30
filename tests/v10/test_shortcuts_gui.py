import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QTextEdit, QWidget

from taskmanager.shortcuts import ShortcutAction, ShortcutController


KEYS = {
    ShortcutAction.QUICK_CAPTURE: "Ctrl+Space",
    ShortcutAction.COMMAND_SEARCH: "Ctrl+K",
    ShortcutAction.NEW_TASK: "N",
    ShortcutAction.TODAY: "T",
    ShortcutAction.TOMORROW: "M",
    ShortcutAction.DELEGATE: "D",
    ShortcutAction.WAIT: "W",
    ShortcutAction.PRIORITY_1: "1",
    ShortcutAction.PRIORITY_2: "2",
    ShortcutAction.PRIORITY_3: "3",
    ShortcutAction.PRIORITY_4: "4",
    ShortcutAction.COMPLETE: "Space",
    ShortcutAction.DELETE: "Del",
    ShortcutAction.UNDO: "Ctrl+Z",
}


@pytest.mark.parametrize("action", list(ShortcutAction))
def test_controller_dispatches_every_action(qtbot, action):
    controller = ShortcutController(QWidget())
    with qtbot.waitSignal(controller.dispatched) as signal:
        assert controller.dispatch(action) is True
    assert signal.args == [action]


@pytest.mark.parametrize("editor_type", [QLineEdit, QTextEdit])
def test_global_actions_are_suppressed_while_editing(qtbot, editor_type):
    host = QWidget()
    editor = editor_type(host)
    qtbot.addWidget(host)
    host.show()
    editor.show()
    editor.setFocus(Qt.FocusReason.OtherFocusReason)
    qtbot.waitUntil(editor.hasFocus)
    controller = ShortcutController(host)
    assert controller.dispatch(ShortcutAction.NEW_TASK) is False


def test_controller_installs_complete_shortcut_map(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    controller = ShortcutController(host)
    assert {action: shortcut.key().toString() for action, shortcut in controller.shortcuts.items()} == KEYS


def test_shell_command_search_is_distinct_from_quick_capture(qtbot, v10_database):
    from taskmanager.repositories import TaskRepository
    from taskmanager.task_store import TaskStore
    from taskmanager.v10_shell import V10Shell
    shell = V10Shell(TaskStore(TaskRepository(v10_database))); qtbot.addWidget(shell); shell.show()
    shell._dispatch_shortcut(ShortcutAction.COMMAND_SEARCH)
    assert shell.command_search.isVisible()
    assert not shell.quick_capture.isVisible()
