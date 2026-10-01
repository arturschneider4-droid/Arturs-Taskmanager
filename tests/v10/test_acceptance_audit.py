"""Real GUI scenarios: persistence across capture, navigation and board actions."""
from dataclasses import replace
from datetime import date, timedelta
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore, SaveTask
from taskmanager.v10_shell import V10Shell
from taskmanager.navigation import Route
from taskmanager.detail_panel import SaveState
from taskmanager.dashboard import DashboardFilter

@pytest.fixture
def app(qtbot, v10_database):
    repo = TaskRepository(v10_database)
    shell = V10Shell(TaskStore(repo)); qtbot.addWidget(shell)
    shell.resize(1366, 768); shell.show()
    return shell, repo


def test_kanban_capture_and_pending_editor_cannot_reset_status(app, qtbot):
    shell, repo = app
    first = repo.save(TaskDraft(title='Prüfbericht freigeben'))
    other = repo.save(TaskDraft(title='Kundenangebot', status='In Arbeit'))
    shell.navigate(Route.KANBAN)
    shell.detail_panel.open_task(first)
    shell.detail_panel.description_edit.setPlainText('Freigabe mit Laborleiter')
    board = shell.page_for(Route.KANBAN)
    assert board.move_task(first, 'In Arbeit')
    shell.show_quick_capture(); shell.quick_capture.input.setText('Neue Anfrage morgen')
    qtbot.keyClick(shell.quick_capture.input, Qt.Key_Return)
    qtbot.wait(350)
    assert repo.get(first).draft.status == 'In Arbeit'
    assert repo.get(first).draft.description == 'Freigabe mit Laborleiter'
    assert repo.get(other).draft.status == 'In Arbeit'
    assert len(repo.query()) == 3


def test_fast_task_switch_flushes_original_draft(app, qtbot):
    shell, repo = app
    a = repo.save(TaskDraft(title='A')); b = repo.save(TaskDraft(title='B'))
    shell.detail_panel.open_task(a)
    shell.detail_panel.title_edit.setText('A geändert')
    shell.detail_panel.open_task(b)
    qtbot.wait(350)
    assert repo.get(a).draft.title == 'A geändert'
    assert repo.get(b).draft.title == 'B'


def test_title_edit_preserves_completed_subtasks(app, qtbot):
    shell, repo = app
    task = repo.save(TaskDraft(title='Bericht', subtasks=(('Messung', True), ('Review', False))))
    shell.detail_panel.open_task(task); shell.detail_panel.title_edit.setText('Bericht final')
    qtbot.waitUntil(lambda: shell.detail_panel.save_state == SaveState.SAVED)
    assert repo.get(task).draft.subtasks == (('Messung', True), ('Review', False))


def test_invalid_draft_blocks_task_switch(app):
    shell, repo = app
    a = repo.save(TaskDraft(title='A')); b = repo.save(TaskDraft(title='B'))
    shell.detail_panel.open_task(a); shell.detail_panel.title_edit.clear()
    shell.detail_panel.open_task(b)
    assert shell.detail_panel.task_id == a
    assert shell.detail_panel.save_state == SaveState.ERROR


@pytest.mark.parametrize('route', [Route.INBOX, Route.KANBAN, Route.EISENHOWER, Route.CALENDAR])
def test_visible_task_opens_details_in_each_view(app, qtbot, route):
    shell, repo = app
    task = repo.save(TaskDraft(title='Kundentermin'))
    shell.navigate(route); page = shell.page_for(route)
    listing = page.list if route == Route.INBOX else page.listing if route == Route.CALENDAR else next(w for w in page.lane_widgets.values() if w.count())
    item = listing.item(0)
    qtbot.mouseClick(listing.viewport(), Qt.LeftButton, pos=listing.visualItemRect(item).center())
    assert shell.detail_panel.task_id == task
    assert shell.detail_panel.isVisible()


def test_small_window_keeps_open_details_accessible(app, qtbot):
    shell, repo = app
    task = repo.save(TaskDraft(title='Kleine Ansicht'))
    shell.resize(720, 640); shell.detail_panel.open_task(task)
    qtbot.wait(50)
    assert shell.detail_panel.isVisible()
    assert shell.detail_panel.width() >= 280


def test_overdue_metric_opens_filtered_tasks(app, qtbot):
    shell, repo = app
    repo.save(TaskDraft(title='Überfällig', deadline=date.today()-timedelta(days=1)))
    repo.save(TaskDraft(title='Zukunft', deadline=date.today()+timedelta(days=10)))
    qtbot.mouseClick(shell.page_for(Route.DASHBOARD).card_for(DashboardFilter.OVERDUE), Qt.LeftButton)
    assert [x.title for x in shell.pages.currentWidget().summaries()] == ['Überfällig']


def test_new_task_has_mouse_accessible_entry(app, qtbot):
    shell, repo = app
    button = shell.findChild(QPushButton, 'new_task')
    assert button is not None, 'New task must be available without knowing a shortcut'
    qtbot.mouseClick(button, Qt.LeftButton)
    assert shell.quick_capture.isVisible()


def test_window_close_flushes_pending_edit(app):
    shell, repo = app
    task = repo.save(TaskDraft(title='Vor Schließen'))
    shell.detail_panel.open_task(task); shell.detail_panel.title_edit.setText('Gespeichert beim Schließen')
    shell.close()
    assert repo.get(task).draft.title == 'Gespeichert beim Schließen'


def test_navigation_has_readable_dark_background(app, qtbot):
    shell, _ = app
    qtbot.wait(20)
    color = shell.navigation.grab().toImage().pixelColor(3, 3)
    assert color.lightness() < 90


def test_detail_exposes_project_and_top_three_and_preserves_them(app, qtbot):
    shell, repo = app
    c = repo._connect(); pid=c.execute("INSERT INTO projects(name) VALUES('Vertrieb')").lastrowid; c.commit(); c.close()
    task=repo.save(TaskDraft(title='Rahmenvertrag', status='In Arbeit'))
    panel=shell.detail_panel; panel.open_task(task)
    assert hasattr(panel, 'project_combo') and hasattr(panel, 'top_three')
    panel.project_combo.setCurrentIndex(panel.project_combo.findData(pid)); panel.top_three.setChecked(True)
    qtbot.waitUntil(lambda: panel.save_state == SaveState.SAVED)
    saved=repo.get(task).draft
    assert saved.project_id == pid and saved.is_top_three and saved.status == 'In Arbeit'


def test_review_goals_are_saved_and_visible_in_weekly_focus(app, qtbot):
    shell, repo=app; shell.navigate(Route.WEEKLY_REVIEW); view=shell.pages.currentWidget()
    for i in range(6):
        view.answer_edit.setText('Entscheidung getroffen'); view.next_button.click()
    view.answer_edit.setText('Angebote abschließen; Teamgespräche; Prüfplanung')
    view.next_button.click()
    assert view.service.goals() == ['Angebote abschließen', 'Teamgespräche', 'Prüfplanung']
    assert 'Angebote abschließen' in shell.weekly_focus.goals_label.text()


def test_review_back_keeps_answer(app):
    shell,_=app;view=shell.page_for(Route.WEEKLY_REVIEW)
    view.answer_edit.setText('Eingang geklärt');view.next_button.click();view.back_button.click()
    assert view.answer_edit.text() == 'Eingang geklärt'


def test_reminder_scheduler_is_running_in_real_shell(app):
    shell,_=app
    assert hasattr(shell,'reminder_scheduler') and shell.reminder_scheduler.timer.isActive()


def test_density_setting_applies_to_shell_immediately(app):
    shell,_=app; view=shell.page_for(Route.SETTINGS)
    old=shell.styleSheet();view.density.setCurrentText('comfortable');view.save_button.click()
    assert shell.styleSheet() != old


def test_monthly_recurrence_generates_one_next_task_and_undo_removes_it(app):
    shell,repo=app
    a=repo.save(TaskDraft(title='Monatsbericht', recurrence='monthly', planning_date=date(2026,1,31)))
    shell.store.apply(SaveTask(replace(repo.get(a).draft,status='Erledigt'),a))
    active=[x for x in repo.query() if x.status != 'Erledigt']
    assert len(active)==1 and active[0].planning_date==date(2026,2,28)
    shell.store.undo()
    assert len(repo.query())==1 and repo.get(a).draft.status=='Offen'


def test_invalid_save_does_not_consume_undo(app):
    shell,repo=app
    for i in range(3):repo.save(TaskDraft(title=f'Top {i}',is_top_three=True))
    a=repo.save(TaskDraft(title='Andere'))
    result=shell.store.apply(SaveTask(replace(repo.get(a).draft,is_top_three=True),a))
    assert not result.ok
    assert not shell.store.undo_manager.can_undo


def test_quick_capture_zero_duration_does_not_raise(app, qtbot):
    shell,repo=app
    shell.show_quick_capture();shell.quick_capture.input.setText('Angebot 0min')
    qtbot.keyClick(shell.quick_capture.input,Qt.Key_Return)
    assert not repo.query()
    assert shell.quick_capture.isVisible()
    assert 'positiv' in shell.quick_capture.preview_label.text()


def test_inbox_excludes_completed_unplanned_tasks(app):
    shell,repo=app
    repo.save(TaskDraft(title='Schon erledigt',status='Erledigt'))
    assert shell.page_for(Route.INBOX).titles()==[]


def test_board_drop_event_persists_only_target_task(app):
    from PySide6.QtCore import QMimeData, QPointF
    from PySide6.QtGui import QDropEvent
    from taskmanager.board_views import BoardLane
    shell,repo=app
    a=repo.save(TaskDraft(title='Verschieben'));b=repo.save(TaskDraft(title='Bleibt',status='In Arbeit'))
    board=shell.page_for(Route.KANBAN)
    mime=QMimeData();mime.setData(BoardLane.MIME,str(a).encode())
    event=QDropEvent(QPointF(10,10),Qt.MoveAction,mime,Qt.LeftButton,Qt.NoModifier)
    board.lane_widgets['In Arbeit'].dropEvent(event)
    assert event.isAccepted()
    assert repo.get(a).draft.status=='In Arbeit' and repo.get(b).draft.status=='In Arbeit'
    shell.store.apply(SaveTask(TaskDraft(title='Neu')))
    assert repo.get(a).draft.status=='In Arbeit'


def test_detail_all_date_control_and_reminder_fields_survive_restart(app,qtbot):
    from PySide6.QtCore import QDate, QDateTime
    from datetime import datetime
    shell,repo=app;task=repo.save(TaskDraft(title='Prüfung'))
    p=shell.detail_panel;p.open_task(task)
    p.planning_enabled.setChecked(True);p.planning_date.setDate(QDate(2026,10,5))
    p.deadline_enabled.setChecked(True);p.deadline_date.setDate(QDate(2026,10,9))
    p.person_edit.setText('Anna');p.control_combo.setCurrentIndex(p.control_combo.findData('delegated'))
    p.follow_up_enabled.setChecked(True);p.follow_up_date.setDate(QDate(2026,10,7))
    p.reminder_enabled.setChecked(True);p.reminder_at.setDateTime(QDateTime(datetime(2026,10,7,9,30)))
    p.estimated_minutes.setValue(60);p.subtasks_edit.setPlainText('[x] Aufbau\n[ ] Auswertung')
    qtbot.waitUntil(lambda:p.save_state==SaveState.SAVED)
    d=TaskRepository(repo.db_path).get(task).draft
    assert (d.planning_date,d.deadline,d.follow_up_date)==(date(2026,10,5),date(2026,10,9),date(2026,10,7))
    assert d.reminder_enabled and d.reminder_at==datetime(2026,10,7,9,30)
    assert d.responsible_party=='Anna' and d.control_mode.value=='delegated'
    assert d.subtasks==(('Aufbau',True),('Auswertung',False))
    p.reminder_enabled.setChecked(False);p.planning_enabled.setChecked(False)
    qtbot.waitUntil(lambda:p.save_state==SaveState.SAVED)
    assert not repo.get(task).draft.reminder_enabled and repo.get(task).draft.reminder_at is None
    assert repo.get(task).draft.planning_date is None and repo.get(task).draft.deadline==date(2026,10,9)


def test_quick_capture_project_token_is_persisted(app,qtbot):
    shell,repo=app
    c=repo._connect();pid=c.execute("INSERT INTO projects(name) VALUES('Vertrieb')").lastrowid;c.commit();c.close()
    shell.show_quick_capture();shell.quick_capture.input.setText('Angebot #Vertrieb morgen')
    qtbot.keyClick(shell.quick_capture.input,Qt.Key_Return)
    d=repo.get(repo.query()[0].id).draft
    assert d.project_id==pid and d.title=='Angebot'


def test_calendar_date_actions_are_reachable_and_keep_deadline_separate(app,qtbot):
    from PySide6.QtCore import QDate
    shell,repo=app;a=repo.save(TaskDraft(title='Planung',deadline=date(2026,10,20)))
    shell.navigate(Route.CALENDAR);view=shell.pages.currentWidget()
    assert hasattr(view,'calendar') and hasattr(view,'plan_button')
    view.listing.setCurrentRow(0);view.calendar.setSelectedDate(QDate(2026,10,6));view.plan_button.click()
    d=repo.get(a).draft
    assert d.planning_date==date(2026,10,6) and d.deadline==date(2026,10,20)


def test_default_reminder_minutes_affects_new_reminder(app):
    from datetime import datetime
    shell,repo=app
    view=shell.page_for(Route.SETTINGS);view.reminder.setValue(90);view.save_button.click()
    task=repo.save(TaskDraft(title='Erinnern'));shell.detail_panel.open_task(task)
    minutes=(shell.detail_panel.reminder_at.dateTime().toPython()-datetime.now()).total_seconds()/60
    assert 89 <= minutes <= 91


def test_next_seven_days_does_not_show_completed_tasks(app):
    shell,repo=app
    repo.save(TaskDraft(title='Erledigt',planning_date=date.today(),status='Erledigt'))
    assert shell.page_for(Route.NEXT_SEVEN).summaries()==[]


def test_refresh_removes_old_rows_from_visible_ui_immediately(app, qtbot):
    from taskmanager.task_list import ListTaskRow
    shell,repo=app;repo.save(TaskDraft(title='Einzige Aufgabe'));shell.navigate(Route.TASKS)
    view=shell.pages.currentWidget();view.refresh()
    visible=[w for w in view.content.findChildren(ListTaskRow) if not w.isHidden()]
    assert len(visible) <= 1
    qtbot.waitUntil(lambda: len([w for w in view.content.findChildren(ListTaskRow) if not w.isHidden()]) == 1)


def test_empty_task_list_has_no_artificial_scroll(app,qtbot):
    shell,_=app;shell.navigate(Route.TASKS);qtbot.wait(20)
    assert shell.pages.currentWidget().scroll_area.verticalScrollBar().maximum()==0


def test_backup_restore_is_accessible_from_settings_and_refreshes_app(app,qtbot):
    shell,repo=app;repo.save(TaskDraft(title='Gesichert'))
    shell.navigate(Route.SETTINGS);view=shell.pages.currentWidget()
    assert hasattr(view,'backup_button') and hasattr(view,'restore_button')
    view.backup_button.click()
    repo.save(TaskDraft(title='Nach Sicherung'))
    view.restore_button.click();dialog=view.restore_dialog
    dialog.restore_button.click()
    assert [x.title for x in repo.query()]==['Gesichert']
    assert shell.page_for(Route.TASKS).summaries()[0].title=='Gesichert'


def test_weekly_goal_completion_updates_progress(app):
    shell,_=app
    from taskmanager.weekly_review import WeeklyReviewService
    WeeklyReviewService(shell.store.repository.db_path).set_goals(['Abschluss'])
    shell.weekly_focus.refresh()
    assert hasattr(shell.weekly_focus,'goal_checks')
    shell.weekly_focus.goal_checks[0].click()
    assert '100' in shell.weekly_focus.progress_label.text()


def test_search_can_be_opened_selected_and_dismissed_by_keyboard(app,qtbot):
    shell,repo=app;a=repo.save(TaskDraft(title='Gezielte Suche'))
    shell.search_button.click();search=shell.command_search
    search.input.setText('Gezielte');search.results.setCurrentRow(0)
    qtbot.keyClick(search.results,Qt.Key_Return)
    assert shell.detail_panel.task_id==a and not search.isVisible()
    shell.search_button.click();qtbot.keyClick(search.input,Qt.Key_Escape)
    assert not search.isVisible()


def test_followup_dashboard_count_includes_self_managed_followups(app,qtbot):
    shell,repo=app
    repo.save(TaskDraft(title='Selbst nachfassen',follow_up_date=date.today()))
    shell.page_for(Route.DASHBOARD).card_for(DashboardFilter.FOLLOW_UPS).click()
    view=shell.pages.currentWidget()
    assert view.tree.topLevelItemCount()==1
    assert view.tree.topLevelItem(0).child(0).text(0)=='Selbst nachfassen'


@pytest.mark.parametrize('route',list(Route))
@pytest.mark.parametrize('size',[(720,640),(1366,768),(1920,1080)])
def test_populated_routes_fit_requested_window_without_forcing_width(app,qtbot,route,size):
    from tests.v10.visual_fixtures import seed_visual_tasks
    shell,repo=app;seed_visual_tasks(repo)
    shell.resize(*size);shell.navigate(route);qtbot.wait(20)
    assert shell.width()==size[0]
    assert shell.navigation.geometry().right() < shell.width()
    assert shell.new_button.isVisible() and shell.new_button.mapTo(shell, shell.new_button.rect().bottomRight()).x() <= shell.width()


def test_narrow_detail_uses_available_width_without_horizontal_scroll(app, qtbot):
    shell, repo = app
    task = repo.save(TaskDraft(title='Schmale Ansicht'))
    shell.resize(720, 640)
    shell.detail_panel.open_task(task)
    qtbot.wait(30)
    assert shell.detail_panel.width() > 500
    assert shell.detail_panel.scroll.horizontalScrollBar().maximum() == 0
