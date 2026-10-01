from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
from pathlib import Path
import shutil
import sqlite3
from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QPushButton, QVBoxLayout


@dataclass(frozen=True)
class BackupPreview:
    path: Path
    task_count: int
    created_at: datetime


class BackupService:
    def __init__(self, db_path: Path, backup_dir: Path):
        self.db_path = Path(db_path); self.backup_dir = Path(backup_dir)
    def create(self, label="manual"):
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        target = self.backup_dir / f"{datetime.now():%Y%m%d_%H%M%S_%f}_{label}.db"
        source = sqlite3.connect(self.db_path); destination = sqlite3.connect(target)
        source.backup(destination); destination.close(); source.close(); return target
    def list(self):
        return sorted(self.backup_dir.glob("*.db"), key=lambda path: path.stat().st_mtime, reverse=True) if self.backup_dir.exists() else []
    def preview(self, path):
        path = Path(path); connection = sqlite3.connect(path)
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            connection.close(); raise ValueError("Backup ist beschädigt")
        count = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]; connection.close()
        return BackupPreview(path, count, datetime.fromtimestamp(path.stat().st_mtime))
    def restore(self, path):
        path = Path(path); self.preview(path); self.create("before_restore")
        temporary = self.db_path.with_suffix(".restore.tmp"); shutil.copy2(path, temporary); temporary.replace(self.db_path)
    def export_csv(self, target):
        target = Path(target); target.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path); connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT title,status,priority,planning_date,deadline,responsible_party FROM tasks ORDER BY id").fetchall(); connection.close()
        with target.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle); writer.writerow(["Titel", "Status", "Priorität", "Planung", "Deadline", "Person"])
            writer.writerows(tuple(row) for row in rows)
        return target


class RestoreDialog(QDialog):
    def __init__(self, service: BackupService, parent=None):
        super().__init__(parent); self.service = service; root = QVBoxLayout(self)
        self.backups = QComboBox(); self.preview_label = QLabel(); self.restore_button = QPushButton("Ausgewähltes Backup wiederherstellen")
        for path in service.list(): self.backups.addItem(path.name, path)
        root.addWidget(self.backups); root.addWidget(self.preview_label); root.addWidget(self.restore_button)
        self.backups.currentIndexChanged.connect(self._preview); self.restore_button.clicked.connect(self._restore); self._preview()
    def _preview(self):
        path = self.backups.currentData()
        self.restore_button.setEnabled(bool(path))
        if not path: self.preview_label.setText("Noch keine Backups vorhanden")
        if path:
            preview = self.service.preview(path); self.preview_label.setText(f"{preview.task_count} Aufgaben · {preview.created_at:%d.%m.%Y %H:%M}\nErsetzt den aktuellen Stand. Vorher wird automatisch eine Sicherung erstellt.")
    def _restore(self):
        path = self.backups.currentData()
        if path: self.service.restore(path); self.accept()
