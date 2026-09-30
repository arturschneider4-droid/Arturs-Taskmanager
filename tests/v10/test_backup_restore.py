import csv

from taskmanager.backup_restore import BackupService
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft


def test_manual_backup_list_preview_and_restore(v10_database, tmp_path):
    repository = TaskRepository(v10_database); repository.save(TaskDraft(title="Vorher"))
    service = BackupService(v10_database, tmp_path / "backups")
    backup = service.create("manual")
    repository.save(TaskDraft(title="Nachher"))
    assert backup in service.list()
    assert service.preview(backup).task_count == 1
    service.restore(backup)
    assert [item.title for item in repository.query()] == ["Vorher"]


def test_export_writes_readable_csv(v10_database, tmp_path):
    repository = TaskRepository(v10_database); repository.save(TaskDraft(title="Export"))
    target = BackupService(v10_database, tmp_path / "backups").export_csv(tmp_path / "tasks.csv")
    with target.open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["Titel"] == "Export"
