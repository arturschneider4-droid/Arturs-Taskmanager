from pathlib import Path

from taskmanager.settings import AppSettings, HelpView, SettingsRepository, SettingsView


class FakeAutostart:
    def __init__(self): self.enabled = False
    def set_enabled(self, enabled): self.enabled = enabled


def test_settings_roundtrip_all_fields_and_corrupt_fallback(tmp_path):
    path = tmp_path / "settings.json"
    repository = SettingsRepository(path)
    expected = AppSettings("my_day", True, 20, "mon-fri", "comfortable", str(tmp_path / "backups"))
    repository.save(expected)
    assert repository.load() == expected
    path.write_text("{broken", encoding="utf-8")
    assert repository.load() == AppSettings()


def test_settings_view_persists_and_controls_autostart(qtbot, tmp_path):
    repository = SettingsRepository(tmp_path / "settings.json")
    adapter = FakeAutostart(); view = SettingsView(repository, adapter)
    qtbot.addWidget(view)
    view.autostart.setChecked(True); view.density.setCurrentText("comfortable"); view.save_button.click()
    assert repository.load().autostart is True
    assert adapter.enabled is True


def test_help_view_documents_shortcuts_and_date_semantics(qtbot):
    view = HelpView(); qtbot.addWidget(view)
    text = view.text.toPlainText()
    assert "Strg + Leertaste" in text
    assert "Planungsdatum" in text and "Deadline" in text


def test_shell_exposes_real_settings_and_help_pages(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.repositories import TaskRepository
    from taskmanager.task_store import TaskStore
    from taskmanager.v10_shell import V10Shell
    shell = V10Shell(TaskStore(TaskRepository(v10_database))); qtbot.addWidget(shell)
    assert isinstance(shell.page_for(Route.SETTINGS), SettingsView)
    assert isinstance(shell.page_for(Route.HELP), HelpView)
