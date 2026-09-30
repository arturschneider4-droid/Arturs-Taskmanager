from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import os
import sys

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget


@dataclass(frozen=True)
class AppSettings:
    start_view: str = "dashboard"
    autostart: bool = False
    default_reminder_minutes: int = 30
    work_week: str = "mon-fri"
    density: str = "compact"
    backup_directory: str = ""


class SettingsRepository:
    def __init__(self, path: Path): self.path = Path(path)
    def load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return AppSettings(**{key: data[key] for key in asdict(AppSettings()) if key in data})
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return AppSettings()
    def save(self, settings: AppSettings):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self.path)


class WindowsAutostartAdapter:
    def __init__(self, app_name="ArtursTaskmanager"): self.app_name = app_name
    def set_enabled(self, enabled):
        if sys.platform != "win32": return
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, f'"{sys.executable}"')
        else:
            try: winreg.DeleteValue(key, self.app_name)
            except FileNotFoundError: pass
        winreg.CloseKey(key)


class SettingsView(QWidget):
    def __init__(self, repository: SettingsRepository, autostart_adapter, parent=None):
        super().__init__(parent); self.repository = repository; self.autostart_adapter = autostart_adapter
        settings = repository.load(); root = QVBoxLayout(self)
        self.autostart = QCheckBox("Mit Windows starten"); self.autostart.setChecked(settings.autostart)
        self.autostart.setObjectName("settings_autostart")
        self.density = QComboBox(); self.density.addItems(["compact", "comfortable"]); self.density.setCurrentText(settings.density)
        self.reminder = QSpinBox(); self.reminder.setRange(0, 1440); self.reminder.setValue(settings.default_reminder_minutes)
        self.save_button = QPushButton("Einstellungen speichern"); self.feedback = QLabel()
        self.save_button.setObjectName("settings_save")
        for widget in (self.autostart, self.density, self.reminder, self.save_button, self.feedback): root.addWidget(widget)
        self.save_button.clicked.connect(self._save)
    def _save(self):
        old = self.repository.load()
        settings = AppSettings(old.start_view, self.autostart.isChecked(), self.reminder.value(), old.work_week, self.density.currentText(), old.backup_directory)
        self.repository.save(settings); self.autostart_adapter.set_enabled(settings.autostart); self.feedback.setText("Gespeichert")


class HelpView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); root = QVBoxLayout(self); self.text = QTextEdit(); self.text.setReadOnly(True)
        self.text.setPlainText("""Tastenkürzel
Strg + Leertaste: Schnellerfassung · Strg + K: Suche · N: neue Aufgabe
T: heute · M: morgen · D: delegieren · W: warten · 1–4: Priorität
Leertaste: erledigen · Entf: löschen · Strg + Z: rückgängig

Planungsdatum legt fest, wann Sie an einer Aufgabe arbeiten. Die Deadline ist die verbindliche Frist.
Delegation und Warten benötigen eine Person sowie eine Wiedervorlage. Backups können in den Einstellungen wiederhergestellt werden.""")
        root.addWidget(self.text)
