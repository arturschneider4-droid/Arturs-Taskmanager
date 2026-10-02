from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import os
import sys

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QCheckBox, QComboBox, QLabel, QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget


@dataclass(frozen=True)
class AppSettings:
    start_view: str = "dashboard"
    autostart: bool = False
    default_reminder_minutes: int = 30
    work_week: str = "mon-fri"
    density: str = "compact"
    backup_directory: str = ""
    weekly_focus_visible: bool = True


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
    settings_saved = Signal(object)
    restored = Signal()
    def __init__(self, repository: SettingsRepository, autostart_adapter, parent=None):
        super().__init__(parent); self.repository = repository; self.autostart_adapter = autostart_adapter
        settings = repository.load(); root = QVBoxLayout(self)
        self.autostart = QCheckBox("Mit Windows starten"); self.autostart.setChecked(settings.autostart)
        self.autostart.setObjectName("settings_autostart")
        self.density = QComboBox(); self.density.addItems(["compact", "comfortable"]); self.density.setCurrentText(settings.density)
        self.reminder = QSpinBox(); self.reminder.setRange(0, 1440); self.reminder.setValue(settings.default_reminder_minutes)
        self.save_button = QPushButton("Einstellungen speichern"); self.feedback = QLabel()
        self.save_button.setObjectName("settings_save")
        root.addWidget(self.autostart)
        root.addWidget(QLabel("Darstellungsdichte")); root.addWidget(self.density)
        self.density.setCurrentIndex(0 if settings.density == "compact" else 1)
        root.addWidget(QLabel("Standard-Erinnerung: Minuten ab jetzt")); root.addWidget(self.reminder)
        root.addWidget(self.save_button); root.addWidget(self.feedback); root.addStretch()
        self.feedback.setWordWrap(True)
        self.save_button.clicked.connect(self._save)

    def enable_backup_controls(self, service, flush):
        self.backup_service = service; self.flush = flush
        self.backup_button = QPushButton("Backup erstellen")
        self.restore_button = QPushButton("Backup auswählen / wiederherstellen")
        self.export_button = QPushButton("Aufgaben als CSV exportieren")
        for widget in (self.backup_button, self.restore_button, self.export_button):
            self.layout().insertWidget(self.layout().count()-1, widget)
        self.backup_button.clicked.connect(self._backup)
        self.restore_button.clicked.connect(self._open_restore)
        self.export_button.clicked.connect(self._export)

    def _backup(self):
        if not self.flush(): return
        try:
            target = self.backup_service.create()
            self.feedback.setText(f"Backup erstellt: {target.name}")
        except (OSError, ValueError) as error: self.feedback.setText(str(error))

    def _open_restore(self):
        if not self.flush(): return
        from .backup_restore import RestoreDialog
        self.restore_dialog = RestoreDialog(self.backup_service, self)
        self.restore_dialog.accepted.connect(self.restored)
        self.restore_dialog.show()

    def _export(self):
        if not self.flush(): return
        target, _ = QFileDialog.getSaveFileName(self, "CSV exportieren", "Aufgaben.csv", "CSV (*.csv)")
        if not target: return
        try:
            self.backup_service.export_csv(target); self.feedback.setText("CSV exportiert")
        except (OSError, ValueError) as error: self.feedback.setText(str(error))

    def _save(self):
        old = self.repository.load()
        settings = replace(old, autostart=self.autostart.isChecked(), default_reminder_minutes=self.reminder.value(), density=self.density.currentText())
        try:
            self.autostart_adapter.set_enabled(settings.autostart)
            self.repository.save(settings)
        except OSError as error:
            self.feedback.setText(f"Speichern fehlgeschlagen: {error}"); return
        self.feedback.setText("Gespeichert"); self.settings_saved.emit(settings)


class HelpView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); root = QVBoxLayout(self); self.text = QTextEdit(); self.text.setReadOnly(True)
        self.text.setPlainText("""Tastenkürzel
Strg + Leertaste: Schnellerfassung · Strg + K: Suche · N: neue Aufgabe
T: heute · M: morgen · D: delegieren · W: warten · 1–4: Priorität
Leertaste: erledigen · Entf: löschen · Strg + Z: rückgängig

Planungsdatum legt fest, wann Sie an einer Aufgabe arbeiten. Die Deadline ist die verbindliche Frist.
Kanban: Karten ziehen oder Rechtsklick zum Statuswechsel. Anklicken öffnet die Details.
Unteraufgaben: [ ] offen, [x] erledigt. Änderungen werden automatisch gespeichert.
Wiederholung: Beim Erledigen wird die nächste Aufgabe angelegt.
Erinnerungen erscheinen bei geöffneter Anwendung, auch nach überfälligem Neustart.
Wochenziele im letzten Review-Schritt durch Semikolon trennen; im Wochenfokus abhaken.
Delegation und Warten benötigen eine Person sowie eine Wiedervorlage. Backups können in den Einstellungen wiederhergestellt werden.""")
        root.addWidget(self.text)
