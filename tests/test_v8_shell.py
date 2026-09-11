from pathlib import Path


def test_v8_shell_module_contains_approved_architecture():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    for token in (
        "V8_STYLE",
        "V8Shell",
        "V8Navigation",
        "V8TaskList",
        "V8DetailPanel",
        "rebuild_v8_shell",
        "install_v8_responsive_behavior",
        "＋  Aufgabe",
        "THEMENGEBIETE",
        "Detail",
    ):
        assert token in text


def test_v8_shell_is_light_enterprise_and_not_emoji_driven():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "#F4F7F9" in text
    assert "#FFFFFF" in text
    assert "#0050A4" in text
    assert "background: #034A70" not in text
    assert "V8.0" in text


def test_app_wires_v8_shell():
    text = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "style_v8" in text
    assert "rebuild_v8_shell" in text
    assert 'VERSION = "8.0"' in text
