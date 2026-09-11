from pathlib import Path


def test_v8_modules_are_explicitly_included_in_windows_package():
    workflow = Path(".github/workflows/build-windows.yml").read_text(encoding="utf-8")
    for module in (
        "taskmanager.v8_kanban",
        "taskmanager.v8_eisenhower",
        "taskmanager.v8_planning",
    ):
        assert f"--hidden-import {module}" in workflow
