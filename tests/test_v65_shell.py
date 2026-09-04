from pathlib import Path


def test_v65_shell_rebuild_entrypoint_is_preserved():
    text = Path("taskmanager/style_v65.py").read_text(encoding="utf-8")
    assert "V65_STYLE" in text
    assert "rebuild_premium_shell" in text
    assert "stack = window.stack" in text
    assert "stack.setParent(None)" in text


def test_v65_shell_has_first_class_navigation_and_overview():
    text = Path("taskmanager/style_v65.py").read_text(encoding="utf-8")
    for token in ("ARBEITSBEREICHE", "ÜBERSICHT", "Themengebiete", "Heute", "Diese Woche", "Später", "Erledigt", "Alle Aufgaben"):
        assert token in text


def test_v65_shell_reuses_existing_functional_widgets():
    text = Path("taskmanager/style_v65.py").read_text(encoding="utf-8")
    for token in ("window.stack", "window.projects", "window.project_search", "window.overview_labels", "window.scope_buttons"):
        assert token in text


def test_v7_replaces_v65_shell_at_runtime():
    app = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "style_v7" in app
    assert "V7_STYLE" in app
    assert 'VERSION = "7.0"' in app
    assert "rebuild_professional_shell" in app
