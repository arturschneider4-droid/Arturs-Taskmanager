from pathlib import Path


def test_v8_windows_packaging_collects_taskmanager_submodules():
    workflow = Path(".github/workflows/build-windows.yml").read_text(encoding="utf-8")
    assert "--collect-submodules taskmanager" in workflow


def test_v8_modules_are_imported_from_packaging_entrypoint():
    main = Path("main.py").read_text(encoding="utf-8")
    assert "from taskmanager import v8_kanban, v8_eisenhower, v8_planning" in main


def test_final_release_packages_excel_support_and_versioned_zip():
    workflow = Path(".github/workflows/build-windows.yml").read_text(encoding="utf-8")
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "openpyxl>=3.1,<4" in requirements
    assert "--collect-submodules openpyxl" in workflow
    assert "ArtursTaskmanager-V8.0-Windows.zip" in workflow
    assert "name: ArtursTaskmanager-V8.0-Windows" in workflow
