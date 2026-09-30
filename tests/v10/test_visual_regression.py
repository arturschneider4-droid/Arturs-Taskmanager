from pathlib import Path
import sys

import pytest
from PySide6.QtGui import QImage

from tests.v10.visual_fixtures import ROUTES, SIZES, baseline_name, render_route


BASELINES = Path(__file__).parent / "baselines"


@pytest.mark.skipif(
    sys.platform == "win32",
    reason=(
        "Pixelgenaue Referenzen werden mit dem Linux-Referenzrenderer geprüft; "
        "Windows-DPI und EXE-Start werden im Release-Build separat geprüft."
    ),
)
@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("size", SIZES)
def test_main_route_matches_reviewed_baseline(qtbot, tmp_path, route, size):
    expected_path = BASELINES / baseline_name(route, size)
    assert expected_path.exists(), f"Nicht freigegebene visuelle Referenz: {expected_path.name}"
    actual_path = render_route(route, size, tmp_path / expected_path.name)
    expected = QImage(str(expected_path)); actual = QImage(str(actual_path))
    assert expected.size() == actual.size()
    assert expected == actual


def test_minimum_size_keeps_navigation_and_content_reachable(qtbot, tmp_path):
    from taskmanager import db
    from taskmanager.migrations import migrate_to_v10
    from taskmanager.repositories import TaskRepository
    from taskmanager.task_store import TaskStore
    from taskmanager.v10_shell import V10Shell
    db.configure_storage(tmp_path / "geometry"); db.init_db(); migrate_to_v10(db.DB_PATH, db.BACKUP_DIR)
    shell = V10Shell(TaskStore(TaskRepository(db.DB_PATH))); qtbot.addWidget(shell); shell.resize(720, 640); shell.show()
    assert shell.navigation.isVisible() and shell.pages.isVisible()
    assert shell.navigation.width() == 64
