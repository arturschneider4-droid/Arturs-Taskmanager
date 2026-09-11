from pathlib import Path


def test_v8_header_resize_mode_uses_pyside6_enum_compatibility():
    text = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "QHeaderView" in text
    assert "QHeaderView.Fixed = QHeaderView.ResizeMode.Fixed" in text


def test_v8_style_does_not_access_header_instance_fixed_attribute():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "horizontalHeader().Fixed" not in text
