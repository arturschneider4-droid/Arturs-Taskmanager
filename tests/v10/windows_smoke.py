from dataclasses import replace
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))

from PySide6.QtWidgets import QApplication

from taskmanager import db
from taskmanager.app import create_v10_window
from taskmanager.migrations import migrate_to_v10
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import SaveTask, TaskStore


def main():
    app = QApplication.instance() or QApplication([])
    root = Path(tempfile.mkdtemp(prefix="arturs-v10-smoke-"))
    db.configure_storage(root); db.init_db(); migrate_to_v10(db.DB_PATH, db.BACKUP_DIR)
    repository = TaskRepository(db.DB_PATH); task_id = repository.save(TaskDraft(title="Release-Smoke"))
    store = TaskStore(repository); window = create_v10_window(db.DB_PATH); window.show(); app.processEvents()
    assert window.windowTitle() == "Arturs Taskmanager V10.0"
    store.apply(SaveTask(replace(repository.get(task_id).draft, status="Erledigt"), task_id))
    assert repository.get(task_id).draft.status == "Erledigt"
    window.close()


if __name__ == "__main__": main()
