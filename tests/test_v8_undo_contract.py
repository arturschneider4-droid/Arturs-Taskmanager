from pathlib import Path

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from taskmanager import app
from taskmanager.ui import MainWindow


def test_v8_startup_does_not_disable_existing_undo_contract():
    text = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "w.undo_button.setEnabled(False)" not in text
    assert "latest_backup()" in text


def test_startup_backup_enables_button_and_internal_undo(monkeypatch):
    assert hasattr(app, "_sync_startup_undo_state")
    monkeypatch.setattr(app, "latest_backup", lambda: Path("startup.db"))
    qt_app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        app._sync_startup_undo_state(window)
        assert window.undo_button.isEnabled() is True
        assert window._undo_available is True
    finally:
        window.close()
        window.deleteLater()
        qt_app.processEvents()


def test_startup_without_backup_disables_button_and_internal_undo(monkeypatch):
    assert hasattr(app, "_sync_startup_undo_state")
    monkeypatch.setattr(app, "latest_backup", lambda: None)
    qt_app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        app._sync_startup_undo_state(window)
        assert window.undo_button.isEnabled() is False
        assert window._undo_available is False
    finally:
        window.close()
        window.deleteLater()
        qt_app.processEvents()
