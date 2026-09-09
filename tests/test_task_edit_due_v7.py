from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGS = ROOT / "taskmanager" / "dialogs.py"
UI = ROOT / "taskmanager" / "ui.py"
DB = ROOT / "taskmanager" / "db.py"


def test_subtask_edit_button_is_selection_aware_and_uses_current_item():
    text = DIALOGS.read_text(encoding="utf-8")
    assert "self.subs.currentItemChanged.connect" in text
    assert "self.edit_sub.setEnabled(False)" in text
    assert "def _update_sub_buttons" in text
    assert "self.edit_sub.setEnabled(item is not None)" in text
    assert "self.edit_sub.clicked.connect(lambda _=False: self.edit_subtask())" in text


def test_task_dialog_supports_explicit_no_due_date():
    text = DIALOGS.read_text(encoding="utf-8")
    assert "self.no_due = QCheckBox(\"Keine Fälligkeit\")" in text
    assert "self.no_due.setChecked(bool(task and not task[\"due_date\"]))" in text
    assert "\"due_date\": None if self.no_due.isChecked()" in text


def test_editor_due_date_is_saved_as_iso_date_or_null():
    text = UI.read_text(encoding="utf-8")
    assert "self.e_due.interpretText()" in text
    assert "\"due_date\": None if self.e_no_due.isChecked() else self.e_due.date().toString(\"yyyy-MM-dd\")" in text


def test_overdue_tasks_are_visibly_distinguished():
    text = UI.read_text(encoding="utf-8")
    assert "due_date < date.today().isoformat()" in text
    assert "THEME_COLORS[\"red\"]" in text


def test_due_filter_does_not_mix_unassigned_dates_into_later_bucket():
    text = DB.read_text(encoding="utf-8")
    assert 'elif due=="Später": sql+=" AND t.due_date>?"' in text
    assert 'elif due=="Ohne Fälligkeit": sql+=" AND t.due_date IS NULL"' in text
