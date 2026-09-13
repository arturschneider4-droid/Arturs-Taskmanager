from pathlib import Path


def test_v8_startup_does_not_disable_existing_undo_contract():
    text = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "w.undo_button.setEnabled(False)" not in text
    assert "latest_backup()" in text
