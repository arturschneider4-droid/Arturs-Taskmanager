"""Named task-list filters stored alongside tasks, including in database backups."""
from dataclasses import replace
import json
import sqlite3

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                              QPushButton, QLabel, QInputDialog, QMessageBox)

from .repositories import QuerySpec


class SavedFilters(QWidget):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.repository = owner.store.repository
        with self.repository._connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS saved_task_views (name TEXT PRIMARY KEY, filters TEXT NOT NULL)')
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout(); root.addLayout(row)
        self.status = self._combo('Status', [('Alle Status', None), ('Offen', 'Offen'), ('In Arbeit', 'In Arbeit'), ('Erledigt', 'Erledigt')], row)
        self.priority = self._combo('Eisenhower-Kategorie', [('Alle Kategorien', None), ('Wichtig & dringend', 'important_urgent'), ('Wichtig', 'important_not_urgent'), ('Dringend', 'not_important_urgent'), ('Später', 'not_important_not_urgent')], row)
        self.deadline = self._combo('Deadline', [('Alle Deadlines', ''), ('Überfällig', 'overdue'), ('Heute', 'today'), ('Nächste 7 Tage', 'next7'), ('Ohne Deadline', 'none')], row)
        row = QHBoxLayout(); root.addLayout(row)
        self.views = QComboBox(); self.views.setAccessibleName('Gespeicherte Filteransichten')
        self.views.setMinimumWidth(120); row.addWidget(self.views, 1)
        self.save = QPushButton('Speichern …'); self.save.clicked.connect(self._save_dialog); row.addWidget(self.save)
        self.delete = QPushButton('Löschen'); self.delete.clicked.connect(self._delete_dialog); row.addWidget(self.delete)
        self.reset = QPushButton('Zurücksetzen'); self.reset.clicked.connect(self._reset); row.addWidget(self.reset)
        self.feedback = QLabel(); self.feedback.setWordWrap(True); root.addWidget(self.feedback)
        self._reload()
        self.views.currentIndexChanged.connect(self._load_selected)
        for combo in (self.status, self.priority, self.deadline): combo.currentIndexChanged.connect(self._changed)

    @staticmethod
    def _combo(name, items, layout):
        combo = QComboBox(); combo.setAccessibleName(name); combo.setToolTip(name)
        for label, value in items: combo.addItem(label, value)
        combo.setMinimumWidth(0)
        combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        combo.setMinimumContentsLength(8)
        layout.addWidget(combo, 1)
        return combo

    def _changed(self):
        self.owner.query_spec = replace(self.owner.query_spec, status=self.status.currentData(),
                                       priority=self.priority.currentData(), deadline_filter=self.deadline.currentData())
        self.owner._visible_count = 20
        self.owner.refresh()

    def sync(self):
        spec = self.owner.query_spec
        for combo, value in ((self.status, spec.status), (self.priority, spec.priority), (self.deadline, spec.deadline_filter)):
            combo.blockSignals(True); combo.setCurrentIndex(max(0, combo.findData(value))); combo.blockSignals(False)
        if self.views.currentData() is not None:
            self.feedback.setText('Filter geändert – zum Aktualisieren erneut unter demselben Namen speichern.' if self._snapshot() != self.views.currentData() else '')

    def _snapshot(self):
        spec = self.owner.query_spec
        return {key: getattr(spec, key) for key in ('project_id', 'without_project', 'status', 'priority', 'deadline_filter')}

    def _reload(self, select=None):
        self.views.blockSignals(True); self.views.clear(); self.views.addItem('Gespeicherte Ansicht wählen', None)
        with self.repository._connect() as c:
            for row in c.execute('SELECT name,filters FROM saved_task_views ORDER BY name COLLATE NOCASE'):
                self.views.addItem(row['name'], json.loads(row['filters']))
        self.views.setCurrentIndex(max(0, self.views.findText(select or '')))
        self.views.blockSignals(False); self.delete.setEnabled(self.views.currentIndex() > 0)

    def _load_selected(self):
        data = self.views.currentData(); self.delete.setEnabled(data is not None)
        if data is None: return
        self.owner.metric_filter = None
        self.owner._visible_count = 20
        self.owner.set_query(QuerySpec(**data))
        self.feedback.setText('')

    def save_named(self, name):
        name = name.strip()
        if not name or len(name) > 80:
            self.feedback.setText('Bitte einen Namen mit 1 bis 80 Zeichen eingeben.'); return
        try:
            with self.repository._connect() as c:
                c.execute('INSERT OR REPLACE INTO saved_task_views(name,filters) VALUES(?,?)', (name, json.dumps(self._snapshot())))
            self._reload(name); self.feedback.setText('Ansicht gespeichert.')
        except (sqlite3.Error, OSError) as error:
            self.feedback.setText(f'Speichern fehlgeschlagen: {error}')

    def _save_dialog(self):
        name, ok = QInputDialog.getText(self, 'Filteransicht speichern', 'Name:', text=self.views.currentText() if self.views.currentIndex() > 0 else '')
        if not ok: return
        if self.views.findText(name.strip()) > 0:
            if QMessageBox.question(self, 'Ansicht aktualisieren', 'Die bestehende Filteransicht mit diesem Namen ersetzen?') != QMessageBox.Yes: return
        self.save_named(name)

    def delete_current(self):
        if self.views.currentIndex() <= 0: return
        try:
            with self.repository._connect() as c:
                c.execute('DELETE FROM saved_task_views WHERE name=?', (self.views.currentText(),))
            self._reload(); self.feedback.setText('Gespeicherte Ansicht gelöscht. Die aktuellen Filter bleiben aktiv.')
        except (sqlite3.Error, OSError) as error:
            self.feedback.setText(f'Löschen fehlgeschlagen: {error}')

    def _delete_dialog(self):
        if QMessageBox.question(self, 'Filteransicht löschen', 'Diese gespeicherte Ansicht löschen? Aufgaben bleiben erhalten.') == QMessageBox.Yes:
            self.delete_current()

    def _reset(self):
        self.views.setCurrentIndex(0); self.owner.metric_filter = None
        self.owner.set_query(QuerySpec()); self.feedback.setText('')
