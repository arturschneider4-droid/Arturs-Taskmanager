from datetime import date

from PySide6.QtCore import Qt

from taskmanager.quick_capture import InboxView, QuickCaptureOverlay, is_clarified
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import ControlMode, TaskDraft
from taskmanager.task_store import TaskStore


def test_quick_capture_enter_saves_title_only_to_inbox(qtbot, v10_database):
    store = TaskStore(TaskRepository(v10_database))
    overlay = QuickCaptureOverlay(store, today=date(2026, 9, 23))
    qtbot.addWidget(overlay)
    overlay.show()
    overlay.input.setText("Neue Idee")
    with qtbot.waitSignal(overlay.saved) as signal:
        qtbot.keyPress(overlay.input, Qt.Key.Key_Return)
    stored = store.repository.get(signal.args[0])
    assert stored.draft.title == "Neue Idee"
    assert is_clarified(stored.draft) is False


def test_quick_capture_escape_discards_and_tab_requests_advanced(qtbot, v10_database):
    overlay = QuickCaptureOverlay(TaskStore(TaskRepository(v10_database)), today=date(2026, 9, 23))
    qtbot.addWidget(overlay)
    overlay.show()
    qtbot.keyPress(overlay.input, Qt.Key.Key_Escape)
    assert overlay.isVisible() is False
    overlay.show()
    with qtbot.waitSignal(overlay.advanced_requested):
        qtbot.keyPress(overlay.input, Qt.Key.Key_Tab)


def test_preview_explains_recognized_values(qtbot, v10_database):
    overlay = QuickCaptureOverlay(TaskStore(TaskRepository(v10_database)), today=date(2026, 9, 23), projects=["Vertrieb"])
    qtbot.addWidget(overlay)
    overlay.input.setText("Angebot morgen #Vertrieb 30min")
    assert "24.09.2026" in overlay.preview_label.text()
    assert "Vertrieb" in overlay.preview_label.text()
    assert "30 Min." in overlay.preview_label.text()


def test_inbox_lists_only_unclarified_tasks(qtbot, v10_database):
    repository = TaskRepository(v10_database)
    repository.save(TaskDraft(title="Ungeklärt"))
    repository.save(TaskDraft(title="Geplant", planning_date=date(2026, 9, 24)))
    view = InboxView(TaskStore(repository))
    qtbot.addWidget(view)
    assert view.titles() == ["Ungeklärt"]


def test_clarification_accepts_plan_follow_up_or_explicit_no_date():
    assert is_clarified(TaskDraft(title="Plan", planning_date=date(2026, 9, 24)))
    assert is_clarified(TaskDraft(title="Warten", control_mode=ControlMode.WAITING, responsible_party="Anna", follow_up_date=date(2026, 9, 24)))
    assert is_clarified(TaskDraft(title="Ohne Termin", status="Ohne Termin"))


def test_shell_ctrl_space_opens_capture_and_inbox_route_is_real(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.v10_shell import V10Shell

    shell = V10Shell(TaskStore(TaskRepository(v10_database)))
    qtbot.addWidget(shell)
    shell.show()
    shell.activateWindow()
    qtbot.waitUntil(shell.isActiveWindow)
    assert isinstance(shell.page_for(Route.INBOX), InboxView)
    assert shell.quick_capture.isVisible() is False
    qtbot.keyClick(shell, Qt.Key.Key_Space, Qt.KeyboardModifier.ControlModifier)
    assert shell.quick_capture.isVisible() is True
    assert shell.quick_capture.input.hasFocus()


def test_advanced_capture_creates_task_and_opens_real_detail(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.v10_shell import V10Shell
    shell = V10Shell(TaskStore(TaskRepository(v10_database))); qtbot.addWidget(shell); shell.show()
    shell.show_quick_capture(); shell.quick_capture.input.setText("Strategiepapier")
    qtbot.keyPress(shell.quick_capture.input, Qt.Key.Key_Tab)
    assert shell.detail_panel.record.draft.title == "Strategiepapier"
    assert shell.context_stack.currentWidget() is shell.detail_panel
