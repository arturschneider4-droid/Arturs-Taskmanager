from pathlib import Path


def test_v65_shell_rebuild_entrypoint_exists():
    text = Path("taskmanager/style_v65.py").read_text(encoding="utf-8")
    assert "V65_STYLE" in text
    assert "rebuild_premium_shell" in text
    assert "QStackedWidget" in text


def test_v65_shell_has_first_class_navigation_and_overview():
    text = Path("taskmanager/style_v65.py").read_text(encoding="utf-8")
    for token in ("Arbeitsbereiche", "ÜBERSICHT", "Themengebiete", "Heute", "Diese Woche", "Später", "Erledigt", "Alle Aufgaben"):
        assert token in text


def test_v65_shell_reuses_existing_functional_widgets():
    text = Path("taskmanager/style_v65.py").read_text(encoding="utf-8")
    for token in ("window.stack", "window.projects", "window.project_search", "window.overview_labels", "window.scope_buttons"):
        assert token in text


def test_v65_version_is_wired():
    app = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "style_v65" in app
    assert 'VERSION = "6.5"' in app
    assert "rebuild_premium_shell" in app
