from pathlib import Path

import pytest


@pytest.fixture
def v10_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    from taskmanager import db

    app_dir = tmp_path / "TaskManager"
    db.configure_storage(app_dir)
    db.init_db()
    from taskmanager.migrations import migrate_to_v10
    migrate_to_v10(db.DB_PATH, db.BACKUP_DIR)

    yield db.DB_PATH

    db.configure_storage(Path.home() / "TaskManager")


@pytest.fixture
def v10_window(qtbot, v10_database):
    from taskmanager.app import configure_main_window
    from taskmanager.ui import MainWindow

    window = configure_main_window(MainWindow())
    qtbot.addWidget(window)
    return window
