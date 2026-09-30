from pathlib import Path

import taskmanager
from taskmanager import db


def test_release_identity_is_v10():
    assert taskmanager.__version__ == "10.0"


def test_v10_database_is_isolated_from_production(v10_database: Path):
    assert v10_database == db.DB_PATH
    assert v10_database.name == "tasks.db"
    assert v10_database.parent.name == "TaskManager"
    assert v10_database.exists()
    assert v10_database.parent != Path.home() / "TaskManager"


def test_v10_window_uses_release_identity(v10_window):
    assert v10_window.windowTitle() == "Arturs Taskmanager V10.0"
