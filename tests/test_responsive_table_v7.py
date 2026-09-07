from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "taskmanager" / "responsive_table_v7.py"
APP = ROOT / "taskmanager" / "app.py"


def test_responsive_table_reserves_space_for_embedded_widgets():
    text = FIX.read_text(encoding="utf-8")
    assert "TASK_FIXED_WIDTHS = {0: 30, 2: 90, 3: 85, 4: 85, 5: 70, 6: 40}" in text
    assert "TASK_LEFT_MIN_WIDTH = 500" in text
    assert "EDITOR_MIN_WIDTH = 300" in text
    assert "table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)" in text


def test_responsive_table_is_wired_after_v7_shell():
    text = APP.read_text(encoding="utf-8")
    assert "from .responsive_table_v7 import configure_responsive_task_area" in text
    assert "configure_responsive_task_area(w)" in text
    assert text.index("rebuild_professional_shell(w)") < text.index("configure_responsive_task_area(w)")
