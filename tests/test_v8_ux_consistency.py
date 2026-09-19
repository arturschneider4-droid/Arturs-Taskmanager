from pathlib import Path


def test_v8_surfaces_share_common_card_tokens():
    for name in ("v8_kanban.py", "v8_eisenhower.py", "v8_planning.py"):
        text = Path("taskmanager", name).read_text(encoding="utf-8")
        assert "#FFFFFF" in text
        assert "#E1E8EC" in text or "#E3E9ED" in text
        assert "border-radius:7px" in text or "border-radius:6px" in text


def test_v8_surfaces_preserve_presentation_only_boundary():
    for name, forbidden in (
        ("v8_kanban.py", "tasks("),
        ("v8_eisenhower.py", "tasks("),
        ("v8_planning.py", "tasks("),
    ):
        text = Path("taskmanager", name).read_text(encoding="utf-8")
        assert forbidden not in text


def test_v8_detail_panel_uses_same_visual_language():
    text = Path("taskmanager/v8_detail_panel.py").read_text(encoding="utf-8")
    assert "#FFFFFF" in text
    assert "#D9E2E8" in text
    assert "#172B3A" in text


def test_v8_shell_defines_shared_surface_tokens():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    for token in ("#FFFFFF", "#DCE4E9", "#172B3A", "#0050A4"):
        assert token in text
