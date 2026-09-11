from pathlib import Path


def test_v8_windows_packaging_collects_taskmanager_submodules():
    workflow = Path(".github/workflows/build-windows.yml").read_text(encoding="utf-8")
    assert "--collect-submodules taskmanager" in workflow
