from pathlib import Path
import tempfile

from PySide6.QtWidgets import QApplication

from taskmanager import db
from taskmanager.migrations import migrate_to_v10
from taskmanager.navigation import Route
from taskmanager.repositories import TaskRepository
from taskmanager.task_store import TaskStore
from taskmanager.v10_shell import V10Shell


SIZES = ((1920, 1080), (1366, 768), (720, 640))
ROUTES = tuple(Route)


def baseline_name(route, size):
    return f"{route.value}-{size[0]}x{size[1]}.png"


def render_route(route: Route, size: tuple[int, int], target: Path):
    app_dir = Path(tempfile.mkdtemp(prefix="v10-visual-"))
    db.configure_storage(app_dir); db.init_db(); migrate_to_v10(db.DB_PATH, db.BACKUP_DIR)
    shell = V10Shell(TaskStore(TaskRepository(db.DB_PATH)))
    shell.resize(*size); shell.navigate(route); shell.show()
    QApplication.processEvents(); QApplication.processEvents()
    target.parent.mkdir(parents=True, exist_ok=True)
    assert shell.grab().save(str(target))
    shell.close()
    return target
