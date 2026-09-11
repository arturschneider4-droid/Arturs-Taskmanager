from pathlib import Path


def test_v8_kanban_presentation_contract_exists():
    text = Path("taskmanager/v8_kanban.py").read_text(encoding="utf-8")
    for token in (
        "V8Kanban",
        "STATUS_LANES",
        "refresh",
        "source_of_truth",
        "responsive",
    ):
        assert token in text


def test_v8_kanban_preserves_existing_status_categories():
    text = Path("taskmanager/v8_kanban.py").read_text(encoding="utf-8")
    for status in ("Offen", "In Arbeit", "Erledigt"):
        assert status in text


def test_v8_kanban_does_not_replace_task_business_logic():
    text = Path("taskmanager/v8_kanban.py").read_text(encoding="utf-8")
    assert "refresh_kanban" not in text
    assert "tasks(" not in text


def test_v8_kanban_is_installed_by_v8_presentation_layer():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "install_v8_kanban" in text
    assert "V8Kanban" in text
