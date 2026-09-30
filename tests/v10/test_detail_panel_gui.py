from datetime import date
from PySide6.QtCore import QDate

import pytest

from taskmanager.detail_panel import DetailPanel, SaveState
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore


@pytest.fixture
def panel(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    task_id = repository.save(TaskDraft(title="Ursprünglicher Titel", deadline=date(2026, 10, 2)))
    widget = DetailPanel(TaskStore(repository))
    qtbot.addWidget(widget)
    widget.open_task(task_id)
    return widget, repository, task_id


def test_detail_panel_contains_all_eight_progressive_sections(panel):
    widget, _, _ = panel
    assert widget.section_names() == (
        "Aufgabe", "Planung und Deadline", "Themengebiet und Priorität",
        "Steuerung", "Wiedervorlage und Person", "Beschreibung",
        "Unteraufgaben", "Erinnerung und Wiederholung",
    )


def test_autosave_persists_latest_rapid_edit_once_stable(panel, qtbot):
    widget, repository, task_id = panel
    widget.title_edit.setText("Erste Fassung")
    widget.title_edit.setText("Finale Fassung")
    assert widget.save_state is SaveState.PENDING
    qtbot.waitUntil(lambda: widget.save_state is SaveState.SAVED, timeout=1000)
    assert repository.get(task_id).draft.title == "Finale Fassung"
    assert widget.saved_revision == widget.edit_revision


def test_save_error_keeps_user_input_and_displays_error(panel, qtbot):
    widget, repository, task_id = panel
    widget.title_edit.setText("   ")
    qtbot.waitUntil(lambda: widget.save_state is SaveState.ERROR, timeout=1000)
    assert widget.title_edit.text() == "   "
    assert repository.get(task_id).draft.title == "Ursprünglicher Titel"
    assert "Titel" in widget.status_label.text()


def test_all_released_detail_fields_are_editable_and_persisted(panel, qtbot):
    widget, repository, task_id = panel
    widget.description_edit.setPlainText("Vorstandsvorlage vorbereiten")
    widget.status_combo.setCurrentText("In Arbeit")
    widget.priority_combo.setCurrentIndex(widget.priority_combo.findData("important_urgent"))
    widget.planning_enabled.setChecked(True); widget.planning_date.setDate(QDate(2026, 9, 30))
    widget.deadline_enabled.setChecked(True); widget.deadline_date.setDate(QDate(2026, 10, 4))
    widget.estimated_minutes.setValue(90)
    widget.recurrence_combo.setCurrentIndex(widget.recurrence_combo.findData("weekly"))
    widget.subtasks_edit.setPlainText("Zahlen prüfen\nFreigabe einholen")
    qtbot.waitUntil(lambda: widget.save_state is SaveState.SAVED, timeout=1500)
    draft = repository.get(task_id).draft
    assert draft.description == "Vorstandsvorlage vorbereiten"
    assert draft.status == "In Arbeit" and draft.priority == "important_urgent"
    assert draft.planning_date == date(2026, 9, 30) and draft.deadline == date(2026, 10, 4)
    assert draft.estimated_minutes == 90 and draft.recurrence == "weekly"
    assert draft.subtasks == (("Zahlen prüfen", False), ("Freigabe einholen", False))
