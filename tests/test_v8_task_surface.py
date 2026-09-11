from pathlib import Path


def test_v8_task_surface_has_premium_row_hierarchy():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
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
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "getattr(window, \"table\", None)" in text
    assert "horizontalHeader()" in text
    assert "setSectionResizeMode" in text


def test_v8_compact_mode_is_explicitly_styled():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "v8Compact" in text
    assert "_v8_compact" in text
