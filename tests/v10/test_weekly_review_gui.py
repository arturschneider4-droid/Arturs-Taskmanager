from datetime import date

from taskmanager.weekly_review import WeeklyReviewService, WeeklyReviewView


TODAY = date(2026, 9, 28)


def test_review_view_back_next_cancel_and_resume(qtbot, v10_database):
    service = WeeklyReviewService(v10_database, today=TODAY)
    view = WeeklyReviewView(service)
    qtbot.addWidget(view)
    view.answer_edit.setText("geprüft")
    view.next_button.click()
    assert service.resume().current_step == 2
    view.back_button.click()
    assert service.resume().current_step == 1
    view.cancel_button.click()
    assert view.isVisible() is False
    resumed = WeeklyReviewView(service)
    qtbot.addWidget(resumed)
    assert resumed.step_number == 1


def test_empty_answer_shows_validation_error(qtbot, v10_database):
    view = WeeklyReviewView(WeeklyReviewService(v10_database, today=TODAY))
    qtbot.addWidget(view)
    view.answer_edit.clear()
    view.next_button.click()
    assert "Bitte" in view.feedback_label.text()


def test_completion_emits_summary_and_navigation(qtbot, v10_database):
    service = WeeklyReviewService(v10_database, today=TODAY)
    view = WeeklyReviewView(service)
    qtbot.addWidget(view)
    for _ in range(6):
        view.answer_edit.setText("ok")
        view.next_button.click()
    view.answer_edit.setText("fertig")
    with qtbot.waitSignal(view.completed):
        view.next_button.click()


def test_shell_weekly_review_route_is_real(qtbot, v10_database):
    from taskmanager.navigation import Route
    from taskmanager.repositories import TaskRepository
    from taskmanager.task_store import TaskStore
    from taskmanager.v10_shell import V10Shell

    shell = V10Shell(TaskStore(TaskRepository(v10_database)))
    qtbot.addWidget(shell)
    assert isinstance(shell.page_for(Route.WEEKLY_REVIEW), WeeklyReviewView)
