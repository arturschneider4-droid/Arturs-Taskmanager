from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_windows_workflow_has_complete_v10_contract():
    workflow = (ROOT / ".github/workflows/build-windows.yml").read_text(encoding="utf-8")
    for required in (
        "release/v10.0-final", "ArtursTaskmanager-V10.0-Windows.zip",
        "SHA256SUMS-V10.0.txt", "taskmanager.weekly_review", "taskmanager.notifications",
        "taskmanager.calendar_view", "taskmanager/assets", "windows_smoke.py",
        "QT_SCALE_FACTOR", "Compress-Archive", "Get-FileHash",
    ):
        assert required in workflow


def test_release_identity_and_documentation_are_v10():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    release = (ROOT / "docs/releases/V10.0-RELEASE.md")
    assert "## V10.0" in readme
    assert release.exists()
    assert "ArtursTaskmanager-V10.0-Windows.zip" in release.read_text(encoding="utf-8")


def test_required_v10_runtime_assets_exist():
    for relative in (
        "taskmanager/v10_shell.py", "taskmanager/weekly_review.py", "taskmanager/notifications.py",
        "taskmanager/calendar_view.py", "taskmanager/assets/icons/dashboard.svg",
    ):
        assert (ROOT / relative).is_file()
