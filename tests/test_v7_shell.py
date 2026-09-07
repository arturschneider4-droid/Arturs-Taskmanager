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


def test_v7_table_layout_is_explicit_and_responsive():
    text = STYLE.read_text(encoding="utf-8")
    assert "setSectionResizeMode(1, QHeaderView.Stretch)" in text
    assert "for column in (2, 3, 4, 5, 6)" in text
    assert "fixed = {0: 34, 2: 105, 3: 88, 4: 92, 5: 80, 6: 44}" in text
    assert "setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)" in text
    assert "setChildrenCollapsible(False)" in text


def test_app_uses_v7_as_active_shell():
    text = APP.read_text(encoding="utf-8")
    assert "style_v7" in text
    assert "rebuild_professional_shell" in text
    assert 'VERSION = "7.0"' in text
