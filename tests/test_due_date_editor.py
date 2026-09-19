from pathlib import Path


UI = Path("taskmanager/ui.py").read_text(encoding="utf-8")
DB = Path("taskmanager/db.py").read_text(encoding="utf-8")


def test_editor_commits_typed_due_date_before_reading_it():
    assert "self.e_due.interpretText()" in UI
    marker = '"due_date": None if self.e_no_due.isChecked() else self.e_due.date().toString("yyyy-MM-dd")'
    assert marker in UI
    assert UI.index("self.e_due.interpretText()") < UI.index(marker)


def test_database_update_includes_due_date_on_task_save():
    assert "due_date" in DB
    assert "UPDATE tasks SET title=?,description=?,project_id=?,priority=?,due_date=?,status=?,recurrence=?,updated_at=?" in DB
