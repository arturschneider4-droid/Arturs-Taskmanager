from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "taskmanager" / "responsive_table_v7.py"
APP = ROOT / "taskmanager" / "app.py"


def test_responsive_table_reserves_space_for_embedded_widgets():
    text = FIX.read_text(encoding="utf-8")
    assert "TASK_FIXED_WIDTHS = {0: 32, 2: 100, 3: 95, 4: 100, 5: 85, 6: 44}" in text
    assert "TASK_LEFT_MIN_WIDTH = 650" in text
    assert "EDITOR_MIN_WIDTH = 340" in text
    assert "EDITOR_MAX_WIDTH = 400" in text
    assert "table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)" in text


def test_responsive_table_is_wired_after_v7_shell():
    text = APP.read_text(encoding="utf-8")
    assert "from .responsive_table_v7 import configure_responsive_task_area" in text
    assert "configure_responsive_task_area(w)" in text
    assert text.index("rebuild_professional_shell(w)") < text.index("configure_responsive_task_area(w)")


def test_final_window_size_prevents_impossible_splitter_layout():
    text = APP.read_text(encoding="utf-8")
    assert "w.setMinimumSize(1260, 760)" in text


def test_embedded_task_controls_are_bounded_to_their_columns():
    text = FIX.read_text(encoding="utf-8")
    assert "setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)" in text
    assert "widget.setMaximumWidth(width - 8)" in text
    assert "table.setCellWidget" in text
