from pathlib import Path


def test_v8_release_candidate_keeps_legacy_task_workflows():
    text = Path("taskmanager/ui.py").read_text(encoding="utf-8")
    for token in (
        "def refresh_tasks",
        "def refresh_kanban",
        "def refresh_eisen",
        "def refresh_plan",
        "def drop_moved",
        "def select_task",
        "def refresh_all",
    ):
        assert token in text


def test_v8_release_candidate_keeps_v8_surface_installation():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    for token in (
        "install_v8_detail_panel",
        "install_v8_kanban",
        "install_v8_eisenhower",
        "install_v8_planning",
        "install_v8_responsive_behavior",
    ):
        assert token in text


def test_v8_release_candidate_keeps_version_8_startup():
    text = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert 'VERSION = "8.0"' in text
    assert "rebuild_professional_shell" in text
    assert "rebuild_v8_shell" in text
