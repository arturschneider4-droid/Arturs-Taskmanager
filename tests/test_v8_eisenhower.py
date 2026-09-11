from pathlib import Path


def test_v8_eisenhower_presentation_contract_exists():
    text = Path("taskmanager/v8_eisenhower.py").read_text(encoding="utf-8")
    for token in (
        "V8Eisenhower",
        "QUADRANTS",
        "apply",
        "source_of_truth",
        "responsive",
    ):
        assert token in text


def test_v8_eisenhower_preserves_existing_priority_categories():
    text = Path("taskmanager/v8_eisenhower.py").read_text(encoding="utf-8")
    for priority in (
        "important_urgent",
        "important_not_urgent",
        "not_important_urgent",
        "not_important_not_urgent",
    ):
        assert priority in text


def test_v8_eisenhower_does_not_replace_task_business_logic():
    text = Path("taskmanager/v8_eisenhower.py").read_text(encoding="utf-8")
    assert "refresh_eisen" not in text
    assert "tasks(" not in text


def test_v8_eisenhower_is_installed_by_v8_presentation_layer():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "install_v8_eisenhower" in text
    assert "V8Eisenhower" in text
