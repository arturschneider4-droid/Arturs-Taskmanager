from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "taskmanager" / "style_v7.py"
APP = ROOT / "taskmanager" / "app.py"


def test_v7_style_exists_with_professional_shell_tokens():
    text = STYLE.read_text(encoding="utf-8")
    assert "V7_STYLE" in text
    assert "v7Topbar" in text
    assert "v7Sidebar" in text
    assert "v7Workspace" in text
    assert "v7Detail" in text
    assert "KPI" not in text


def test_v7_shell_is_compact_and_not_dashboard_heavy():
    text = STYLE.read_text(encoding="utf-8")
    assert "setFixedHeight(56)" in text
    assert "setFixedWidth(214)" in text
    assert "setObjectName(\"v7Detail\")" in text


def test_app_uses_v7_as_active_shell():
    text = APP.read_text(encoding="utf-8")
    assert "style_v7" in text
    assert "rebuild_professional_shell" in text
    assert 'VERSION = "7.0"' in text
