from pathlib import Path


def test_v8_header_resize_mode_uses_pyside6_enum_compatibility():
    text = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "QHeaderView" in text
    assert "QHeaderView.Fixed = QHeaderView.ResizeMode.Fixed" in text


def test_v8_style_does_not_access_header_instance_fixed_attribute():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "horizontalHeader().Fixed" not in text


def test_v8_list_widgets_use_explicit_qt_selection_enum():
    kanban = Path("taskmanager/v8_kanban.py").read_text(encoding="utf-8")
    eisenhower = Path("taskmanager/v8_eisenhower.py").read_text(encoding="utf-8")
    assert "QAbstractItemView" in kanban
    assert "QAbstractItemView.SelectionMode.SingleSelection" in kanban
    assert "QAbstractItemView" in eisenhower
    assert "QAbstractItemView.SelectionMode.SingleSelection" in eisenhower
    assert "lane.SelectionMode.SingleSelection" not in kanban
    assert "lane.SelectionMode.SingleSelection" not in eisenhower
