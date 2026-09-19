from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "taskmanager" / "ui.py"
DIALOGS = ROOT / "taskmanager" / "dialogs.py"
V7 = ROOT / "taskmanager" / "style_v7.py"


def test_main_task_controls_are_connected():
    text = UI.read_text(encoding="utf-8")
    required = [
        "self.global_search.textChanged.connect(self._sync_global_search)",
        "new.clicked.connect(self.new_task)",
        "self.undo_button.clicked.connect(self.undo_last)",
        "self.projects.itemClicked.connect",
        "self.projects.customContextMenuRequested.connect(self.project_menu)",
        "self.theme_filter.currentIndexChanged.connect(self._theme_filter_changed)",
        "sort.clicked.connect(self.cycle_sort)",
        "self.search.textChanged.connect(self.refresh_all)",
        "self.pfilter.currentIndexChanged.connect(self.refresh_all)",
        "self.sfilter.currentIndexChanged.connect(self.refresh_all)",
        "self.dfilter.currentIndexChanged.connect(self.refresh_all)",
        "self.table.itemSelectionChanged.connect(self.table_selected)",
        "self.table.cellDoubleClicked.connect",
        "self.table.customContextMenuRequested.connect(self.task_menu)",
    ]
    for token in required:
        assert token in text, token


def test_editor_controls_are_connected():
    text = UI.read_text(encoding="utf-8")
    required = [
        "b.clicked.connect(lambda _, k=key: self._editor_priority(k))",
        "self.e_no_due.toggled.connect(self.e_due.setDisabled)",
        "self.e_subs.itemChanged.connect(self.update_sub_count)",
        "self.e_subs.itemDoubleClicked.connect(self.edit_editor_sub)",
        "add.clicked.connect(self.add_editor_sub)",
        "edit.clicked.connect(self.edit_editor_sub)",
        "rem.clicked.connect(self.remove_editor_sub)",
        "save_b.clicked.connect(self.save_editor)",
        "cancel.clicked.connect(lambda: self.select_task(self.selected_task) if self.selected_task else None)",
    ]
    for token in required:
        assert token in text, token


def test_dialog_controls_are_connected():
    text = DIALOGS.read_text(encoding="utf-8")
    required = [
        "self.no_due.toggled.connect(self.due.setDisabled)",
        "self.subs.itemDoubleClicked.connect(self.edit_subtask)",
        "self.subs.currentItemChanged.connect(self._update_sub_buttons)",
        "add.clicked.connect(self.add_sub)",
        "self.edit_sub.clicked.connect(lambda _=False: self.edit_subtask())",
        "remove.clicked.connect(self.remove_sub)",
        "b.accepted.connect(self.accept)",
        "b.rejected.connect(self.reject)",
    ]
    for token in required:
        assert token in text, token


def test_v7_shell_exposes_only_functional_navigation_targets():
    text = V7.read_text(encoding="utf-8")
    for key in ("tasks", "kanban", "eisenhower", "planning", "themes"):
        assert f'"{key}"' in text
    assert "button.clicked.connect(lambda _=False, k=key: window.set_view(k))" in text
    assert "add.clicked.connect(window.new_project)" in text
    assert "edit.clicked.connect" in text
    assert "remove.clicked.connect" in text
