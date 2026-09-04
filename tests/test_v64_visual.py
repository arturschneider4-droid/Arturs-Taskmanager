from pathlib import Path


STYLE = Path("taskmanager/style_v64.py").read_text(encoding="utf-8")
APP = Path("taskmanager/app.py").read_text(encoding="utf-8")
UI = Path("taskmanager/ui.py").read_text(encoding="utf-8")


def test_v64_design_system_is_active():
    assert "V64_STYLE" in STYLE
    assert "apply_v64_visuals" in STYLE
    assert "V64_STYLE" in APP
    assert 'VERSION = "6.4"' in APP


def test_v64_has_premium_surface_hierarchy():
    for token in ("#F4F7FA", "#FFFFFF", "#083E5A", "#0050A4", "QMenu", "QTableWidget"):
        assert token in STYLE


def test_priority_cards_have_non_clipping_height():
    assert "min-height: 88px" in STYLE


def test_task_rows_have_non_clipping_height():
    assert "setDefaultSectionSize(60)" in STYLE


def test_themes_navigation_has_dedicated_workspace_adapter():
    assert "_build_themes_page" in STYLE
    assert 'key == "themes"' in STYLE
    assert "window.stack.addWidget(page)" in STYLE


def test_existing_functional_views_remain_present():
    for name in ("kanban_page", "eisen_page", "plan_page", "refresh_all", "new_project", "edit_project", "delete_project"):
        assert f"def {name}" in UI
