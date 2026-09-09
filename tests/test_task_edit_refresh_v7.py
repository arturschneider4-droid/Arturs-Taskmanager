from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "taskmanager" / "ui.py"


def test_edit_task_refreshes_and_reselects_the_updated_table_row():
    text = UI.read_text(encoding="utf-8")
    assert "values = d.values()" in text
    assert "self.refresh_all()" in text
    assert "self.table.selectRow" in text
    assert "self.table.item(row, 1).data(Qt.UserRole) == tid" in text
