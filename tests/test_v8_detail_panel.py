from pathlib import Path


def test_v8_detail_panel_contract_exists():
    text = Path("taskmanager/v8_detail_panel.py").read_text(encoding="utf-8")
    for token in (
        "class V8DetailPanel",
        "set_task_id",
        "clear_task",
        "set_panel_open",
        "set_panel_width",
        "task_id",
        "panel_open",
        "panel_width",
        "NARROW_BREAKPOINT = 960",
    ):
        assert token in text


def test_v8_detail_panel_width_contract():
    text = Path("taskmanager/v8_detail_panel.py").read_text(encoding="utf-8")
    assert "MIN_WIDTH = 320" in text
    assert "MAX_WIDTH = 650" in text
    assert "DEFAULT_WIDTH = 380" in text


def test_v8_detail_panel_is_installed_by_presentation_layer():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "install_v8_detail_panel" in text
    assert "_toggle_detail" in text
