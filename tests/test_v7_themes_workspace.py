from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "taskmanager" / "style_v7.py"


def test_v7_has_a_dedicated_themes_workspace():
    text = STYLE.read_text(encoding="utf-8")
    assert "def _build_themes_workspace(window):" in text
    assert "v7ThemesWorkspace" in text
    assert "refresh_themes_workspace" in text


def test_themes_navigation_is_a_real_stack_view():
    text = STYLE.read_text(encoding="utf-8")
    assert '"themes": 4' in text
    assert '"themes": "Themengebiete"' in text
    assert 'window.stack.addWidget(themes_page)' in text


def test_themes_workspace_exposes_create_edit_delete_actions():
    text = STYLE.read_text(encoding="utf-8")
    assert "window.new_project" in text
    assert "window.edit_project" in text
    assert "window.delete_project" in text
