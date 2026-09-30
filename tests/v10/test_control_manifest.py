from tests.v10.control_manifest import CONTROL_MANIFEST
from PySide6.QtCore import QObject
from taskmanager.navigation import Route
from taskmanager.repositories import TaskRepository
from taskmanager.task_store import TaskStore
from taskmanager.v10_shell import V10Shell


def test_control_manifest_is_complete_and_unambiguous():
    assert CONTROL_MANIFEST
    names = [row[1] for row in CONTROL_MANIFEST]
    assert len(names) == len(set(names))
    for row in CONTROL_MANIFEST:
        assert len(row) == 6
        assert all(str(value).strip() for value in row)
        assert row[5].startswith("test_")


def test_every_manifest_control_exists_with_stable_object_name(qtbot, v10_database):
    shell = V10Shell(TaskStore(TaskRepository(v10_database))); qtbot.addWidget(shell)
    for route in Route: shell.page_for(route)
    missing = [name for _surface, name, *_rest in CONTROL_MANIFEST if shell.findChild(QObject, name) is None]
    assert missing == []
