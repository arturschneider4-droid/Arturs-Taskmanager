from pathlib import Path


def test_v8_planning_presentation_contract_exists():
    text = Path("taskmanager/v8_planning.py").read_text(encoding="utf-8")
    for token in ("V8Planning", "PLANNING_LANES", "responsive", "source_of_truth"):
        assert token in text


def test_v8_planning_preserves_existing_planning_groups():
    text = Path("taskmanager/v8_planning.py").read_text(encoding="utf-8")
    for group in ("Heute", "Diese Woche", "Später"):
        assert group in text


def test_v8_planning_does_not_replace_task_refresh_logic():
    text = Path("taskmanager/v8_planning.py").read_text(encoding="utf-8")
    assert "refresh_plan" not in text
    assert "tasks(" not in text


def test_v8_planning_is_installed_by_v8_presentation_layer():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "install_v8_planning" in text
    assert "V8Planning" in text
