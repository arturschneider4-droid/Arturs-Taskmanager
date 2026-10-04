from datetime import date, timedelta
from taskmanager.repositories import TaskRepository, QuerySpec
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore
from taskmanager.task_list import TaskListView


def test_saved_view_survives_restart_and_can_be_updated_deleted(qtbot, v10_database):
    repo = TaskRepository(v10_database)
    with repo._connect() as c:
        project = c.execute("INSERT INTO projects(name) VALUES('Labor')").lastrowid
    repo.save(TaskDraft(project_id=project, title='Fällig', status='In Arbeit', priority='important_urgent', deadline=date.today()))
    repo.save(TaskDraft(title='Andere', status='Offen'))
    view = TaskListView(TaskStore(repo), theme_filter=True); qtbot.addWidget(view)
    assert hasattr(view, 'saved_filters')
    view.theme_filter.setCurrentIndex(view.theme_filter.findData(project))
    panel = view.saved_filters
    panel.status.setCurrentText('In Arbeit')
    panel.priority.setCurrentIndex(panel.priority.findData('important_urgent'))
    panel.deadline.setCurrentIndex(panel.deadline.findData('today'))
    assert [r.task.title for r in view._rows] == ['Fällig']
    panel.save_named('Heute wichtig')
    second = TaskListView(TaskStore(repo), theme_filter=True); qtbot.addWidget(second)
    second.saved_filters.views.setCurrentText('Heute wichtig')
    assert second.theme_filter.currentData() == project
    assert [r.task.title for r in second._rows] == ['Fällig']
    second.saved_filters.reset.click()
    assert len(second._rows) == 2
    second.saved_filters.views.setCurrentText('Heute wichtig')
    second.saved_filters.status.setCurrentText('Offen')
    second.saved_filters.save_named('Heute wichtig')
    third = TaskListView(TaskStore(repo), theme_filter=True); qtbot.addWidget(third)
    third.saved_filters.views.setCurrentText('Heute wichtig')
    assert not third._rows
    third.saved_filters.delete_current()
    fourth = TaskListView(TaskStore(repo), theme_filter=True); qtbot.addWidget(fourth)
    assert fourth.saved_filters.views.findText('Heute wichtig') == -1


def test_deadline_filter_is_relative_and_combines_with_theme(v10_database):
    repo=TaskRepository(v10_database)
    repo.save(TaskDraft(title='Gestern', deadline=date(2026,10,3)))
    repo.save(TaskDraft(title='Heute', deadline=date(2026,10,4)))
    repo.save(TaskDraft(title='Später', deadline=date(2026,10,12)))
    repo.save(TaskDraft(title='Ohne'))
    assert [t.title for t in repo.query(QuerySpec(deadline_filter='today', today=date(2026,10,4)))] == ['Heute']
    assert [t.title for t in repo.query(QuerySpec(deadline_filter='overdue', today=date(2026,10,4)))] == ['Gestern']
    assert [t.title for t in repo.query(QuerySpec(deadline_filter='none'))] == ['Ohne']
