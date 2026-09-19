from pathlib import Path


def test_v8_task_surface_has_premium_row_hierarchy():
    text = Path("taskmanager/v8_detail_panel.py").read_text(encoding="utf-8")
    for token in (
        "v8TaskRow",
        "v8TaskTitle",
        "v8TaskMeta",
        "v8TaskStatus",
        "v8TaskPriority",
        "v8TaskDue",
    ):
        assert token in text


def test_v8_task_surface_keeps_functional_table_as_source_of_truth():
    detail = Path("taskmanager/v8_detail_panel.py").read_text(encoding="utf-8")
    style = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert 'getattr(window, "table", None)' in detail
    assert "setHorizontalScrollBarPolicy" in detail
    assert "setSectionResizeMode" in style


def test_v8_compact_mode_is_explicitly_styled():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "_v8_compact" in text
    assert "setDefaultSectionSize(30 if window._v8_compact else 42)" in text
