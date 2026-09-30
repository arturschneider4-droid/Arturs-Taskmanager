from pathlib import Path

import taskmanager
from taskmanager import app
from taskmanager.constants import UI_SPEC


def test_v10_release_identity_and_undo_dependency_are_importable():
    assert app.VERSION == "10.0"
    assert callable(app.latest_backup)
    assert "#v8" in app.V8_STYLE.lower()


def test_v8_startup_uses_a_resolved_latest_backup_function():
    # The startup path calls latest_backup() after the V8 shell is built. Keep
    # the dependency explicit so a packaging/build-only test cannot miss a
    # runtime NameError in the application entry point.
    assert app.latest_backup.__module__ == "taskmanager.db"


def test_v10_runtime_identity_and_release_surface_are_consistent():
    assert taskmanager.__version__ == "10.0"
    assert UI_SPEC["version"] == "V10.0"
    assert "## V10.0" in Path("README.md").read_text(encoding="utf-8")
