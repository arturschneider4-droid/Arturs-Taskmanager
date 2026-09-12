from pathlib import Path


def test_v8_windows_packaging_collects_taskmanager_submodules():
    workflow = Path(".github/workflows/build-windows.yml").read_text(encoding="utf-8")
    assert "--collect-submodules taskmanager" in workflow


def test_v8_modules_are_imported_from_packaging_entrypoint():
    main = Path("main.py").read_text(encoding="utf-8")
    for module in ("v8_kanban", "v8_eisenhower", "v8_planning"):
        assert f"from taskmanager import {module}" in main
