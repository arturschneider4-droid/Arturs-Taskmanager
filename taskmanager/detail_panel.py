from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime
from enum import Enum

from PySide6.QtCore import QDate, QDateTime, QTimer, Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QDateTimeEdit, QFormLayout, QFrame, QLabel, QLineEdit, QPushButton, QScrollArea, QSpinBox, QTextEdit, QVBoxLayout, QWidget

from .task_store import SaveTask, TaskStore


class SaveState(str, Enum):
    IDLE = "idle"
    PENDING = "pending"
    SAVING = "saving"
    SAVED = "saved"
    ERROR = "error"


SECTION_NAMES = (
    "Aufgabe", "Planung und Deadline", "Themengebiet und Priorität",
    "Steuerung", "Wiedervorlage und Person", "Beschreibung",
    "Unteraufgaben", "Erinnerung und Wiederholung",
)


class DetailPanel(QFrame):
    opened = Signal(int)
    close_requested = Signal()

    def __init__(self, store: TaskStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.task_id = None
        self.record = None
        self.save_state = SaveState.IDLE
        self.edit_revision = 0
        self.saved_revision = 0
        self._loading = False
        self.setObjectName("v10DetailPanel")
        root = QVBoxLayout(self)
        header = QFormLayout()
        self.close_button = QPushButton("Schließen")
        self.close_button.setObjectName("detail_close")
        self.close_button.clicked.connect(self.close_requested)
        header.addRow(QLabel("Aufgabendetails"), self.close_button)
        root.addLayout(header)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        content = QWidget()
        self.sections_layout = QVBoxLayout(content)
        self._sections = []
        for name in SECTION_NAMES:
            section = QFrame()
            section.setObjectName("detail_" + name.lower().replace(" ", "_"))
            section_layout = QVBoxLayout(section)
            section_layout.addWidget(QLabel(name))
            if name == "Aufgabe":
                self.title_edit = QLineEdit()
                self.title_edit.setObjectName("detail_title")
                section_layout.addWidget(self.title_edit)
                self.status_combo = QComboBox(); self.status_combo.addItems(["Offen", "In Arbeit", "Erledigt", "Ohne Termin"])
                section_layout.addWidget(self.status_combo)
            elif name == "Planung und Deadline":
                self.planning_enabled = QCheckBox("Planungsdatum verwenden"); self.planning_date = QDateEdit(); self.planning_date.setCalendarPopup(True)
                self.deadline_enabled = QCheckBox("Deadline verwenden"); self.deadline_date = QDateEdit(); self.deadline_date.setCalendarPopup(True)
                self.estimated_minutes = QSpinBox(); self.estimated_minutes.setRange(0, 100000); self.estimated_minutes.setSuffix(" Min.")
                for widget in (self.planning_enabled, self.planning_date, self.deadline_enabled, self.deadline_date, QLabel("Geschätzter Aufwand"), self.estimated_minutes): section_layout.addWidget(widget)
            elif name == "Themengebiet und Priorität":
                self.priority_combo = QComboBox()
                for label, value in (("Wichtig & dringend", "important_urgent"), ("Wichtig", "important_not_urgent"), ("Dringend", "not_important_urgent"), ("Später", "not_important_not_urgent")): self.priority_combo.addItem(label, value)
                section_layout.addWidget(self.priority_combo)
            elif name == "Steuerung":
                self.control_combo = QComboBox(); self.control_combo.addItem("Selbst", "self"); self.control_combo.addItem("Delegiert", "delegated"); self.control_combo.addItem("Warten auf", "waiting")
                section_layout.addWidget(self.control_combo)
            elif name == "Wiedervorlage und Person":
                self.person_edit = QLineEdit(); self.person_edit.setPlaceholderText("Person oder Organisation")
                self.follow_up_enabled = QCheckBox("Wiedervorlage verwenden"); self.follow_up_date = QDateEdit(); self.follow_up_date.setCalendarPopup(True)
                section_layout.addWidget(self.person_edit); section_layout.addWidget(self.follow_up_enabled); section_layout.addWidget(self.follow_up_date)
            elif name == "Beschreibung":
                self.description_edit = QTextEdit(); self.description_edit.setMinimumHeight(90); section_layout.addWidget(self.description_edit)
            elif name == "Unteraufgaben":
                self.subtasks_edit = QTextEdit(); self.subtasks_edit.setPlaceholderText("Eine Unteraufgabe pro Zeile"); self.subtasks_edit.setMinimumHeight(80); section_layout.addWidget(self.subtasks_edit)
            elif name == "Erinnerung und Wiederholung":
                self.reminder_enabled = QCheckBox("Individuelle Erinnerung"); self.reminder_at = QDateTimeEdit(); self.reminder_at.setCalendarPopup(True)
                self.recurrence_combo = QComboBox()
                for label, value in (("Keine", "none"), ("Täglich", "daily"), ("Wöchentlich", "weekly"), ("Monatlich", "monthly")): self.recurrence_combo.addItem(label, value)
                section_layout.addWidget(self.reminder_enabled); section_layout.addWidget(self.reminder_at); section_layout.addWidget(self.recurrence_combo)
            self._sections.append((name, section))
            self.sections_layout.addWidget(section)
        self.sections_layout.addStretch(1)
        self.scroll.setWidget(content)
        root.addWidget(self.scroll, 1)
        self.status_label = QLabel("")
        self.status_label.setObjectName("detail_save_status")
        root.addWidget(self.status_label)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(250)
        self._save_timer.timeout.connect(self._save)
        self.title_edit.textChanged.connect(self._queue_save)
        for widget, signal in (
            (self.status_combo, self.status_combo.currentIndexChanged), (self.priority_combo, self.priority_combo.currentIndexChanged),
            (self.planning_enabled, self.planning_enabled.toggled), (self.planning_date, self.planning_date.dateChanged),
            (self.deadline_enabled, self.deadline_enabled.toggled), (self.deadline_date, self.deadline_date.dateChanged),
            (self.estimated_minutes, self.estimated_minutes.valueChanged), (self.control_combo, self.control_combo.currentIndexChanged),
            (self.person_edit, self.person_edit.textChanged), (self.follow_up_enabled, self.follow_up_enabled.toggled),
            (self.follow_up_date, self.follow_up_date.dateChanged), (self.description_edit, self.description_edit.textChanged),
            (self.subtasks_edit, self.subtasks_edit.textChanged), (self.reminder_enabled, self.reminder_enabled.toggled),
            (self.reminder_at, self.reminder_at.dateTimeChanged), (self.recurrence_combo, self.recurrence_combo.currentIndexChanged),
        ):
            signal.connect(lambda *_args: self._queue_save())

    def section_names(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self._sections)

    def open_task(self, task_id: int) -> None:
        self.task_id = task_id
        self.record = self.store.repository.get(task_id)
        self._loading = True
        if self.record:
            draft = self.record.draft
            self.title_edit.setText(draft.title); self.description_edit.setPlainText(draft.description)
            self.status_combo.setCurrentText(draft.status)
            self.priority_combo.setCurrentIndex(max(0, self.priority_combo.findData(draft.priority)))
            self.planning_enabled.setChecked(draft.planning_date is not None); self.planning_date.setDate(QDate(draft.planning_date or date.today()))
            self.deadline_enabled.setChecked(draft.deadline is not None); self.deadline_date.setDate(QDate(draft.deadline or date.today()))
            self.estimated_minutes.setValue(draft.estimated_minutes or 0)
            self.control_combo.setCurrentIndex(max(0, self.control_combo.findData(draft.control_mode.value)))
            self.person_edit.setText(draft.responsible_party or "")
            self.follow_up_enabled.setChecked(draft.follow_up_date is not None); self.follow_up_date.setDate(QDate(draft.follow_up_date or date.today()))
            self.subtasks_edit.setPlainText("\n".join(title for title, _done in draft.subtasks))
            self.reminder_enabled.setChecked(draft.reminder_enabled)
            self.reminder_at.setDateTime(QDateTime(draft.reminder_at or datetime.now()))
            self.recurrence_combo.setCurrentIndex(max(0, self.recurrence_combo.findData(draft.recurrence)))
        self._loading = False
        self.save_state = SaveState.IDLE
        self.status_label.setText("")
        self.opened.emit(task_id)

    def _queue_save(self) -> None:
        if self._loading or self.record is None:
            return
        self.edit_revision += 1
        self.save_state = SaveState.PENDING
        self.status_label.setText("Änderungen offen")
        self._save_timer.start()

    def _save(self) -> None:
        revision = self.edit_revision
        self.save_state = SaveState.SAVING
        self.status_label.setText("Speichern …")
        try:
            subtasks = tuple((line.strip(), False) for line in self.subtasks_edit.toPlainText().splitlines() if line.strip())
            draft = replace(
                self.record.draft, title=self.title_edit.text(), description=self.description_edit.toPlainText(),
                status=self.status_combo.currentText(), priority=self.priority_combo.currentData(),
                planning_date=self.planning_date.date().toPython() if self.planning_enabled.isChecked() else None,
                deadline=self.deadline_date.date().toPython() if self.deadline_enabled.isChecked() else None,
                estimated_minutes=self.estimated_minutes.value() or None,
                control_mode=self.control_combo.currentData(), responsible_party=self.person_edit.text() or None,
                follow_up_date=self.follow_up_date.date().toPython() if self.follow_up_enabled.isChecked() else None,
                subtasks=subtasks, recurrence=self.recurrence_combo.currentData(),
                reminder_enabled=self.reminder_enabled.isChecked(),
                reminder_at=self.reminder_at.dateTime().toPython() if self.reminder_enabled.isChecked() else None,
            )
        except ValueError as error:
            self.save_state = SaveState.ERROR
            self.status_label.setText(str(error))
            return
        result = self.store.apply(SaveTask(draft, self.task_id))
        if not result.ok:
            self.save_state = SaveState.ERROR
            self.status_label.setText(result.message or "Speichern fehlgeschlagen")
            return
        if revision == self.edit_revision:
            self.record = self.store.repository.get(self.task_id)
            self.saved_revision = revision
            self.save_state = SaveState.SAVED
            self.status_label.setText("Gespeichert")
