from PySide6.QtCore import Qt

from taskmanager.components import Chip, EmptyState, IconButton, MetricCard, PrimaryButton, TaskRow, Toast


def test_buttons_are_keyboard_focusable_and_accessibly_named(qtbot):
    primary = PrimaryButton("Aufgabe anlegen")
    icon = IconButton("plus", "Aufgabe hinzufügen")
    qtbot.addWidget(primary)
    qtbot.addWidget(icon)
    assert primary.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert icon.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert primary.accessibleName() == "Aufgabe anlegen"
    assert icon.accessibleName() == "Aufgabe hinzufügen"


def test_metric_card_emits_its_filter_key_when_activated(qtbot):
    card = MetricCard("Überfällig", 4, "overdue")
    qtbot.addWidget(card)
    with qtbot.waitSignal(card.activated) as signal:
        qtbot.mouseClick(card, Qt.MouseButton.LeftButton)
    assert signal.args == ["overdue"]
    assert card.accessibleName() == "Überfällig: 4"


def test_task_row_exposes_selection_and_complete_actions(qtbot):
    row = TaskRow(17, "Angebot Müller freigeben", "Vertrieb", "Heute")
    qtbot.addWidget(row)
    with qtbot.waitSignal(row.selected) as selected:
        qtbot.mouseClick(row.title_button, Qt.MouseButton.LeftButton)
    with qtbot.waitSignal(row.completed) as completed:
        qtbot.mouseClick(row.complete_button, Qt.MouseButton.LeftButton)
    assert selected.args == [17]
    assert completed.args == [17]
    assert row.title_button.text() == "Angebot Müller freigeben"


def test_component_states_are_explicit_and_styleable(qtbot):
    chip = Chip("Heute")
    toast = Toast("Gespeichert")
    empty = EmptyState("Keine Aufgaben", "Neue Aufgabe", "plus")
    for widget in (chip, toast, empty):
        qtbot.addWidget(widget)
    chip.set_state("error")
    toast.set_state("loading")
    assert chip.property("state") == "error"
    assert toast.property("state") == "loading"
    assert empty.action_button.accessibleName() == "Neue Aufgabe"
