from dataclasses import replace
from PySide6.QtWidgets import QComboBox
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore, SaveTask
from taskmanager.v10_shell import V10Shell
from taskmanager.navigation import Route


def test_theme_filter_select_reset_and_refresh(qtbot, v10_database):
    repo = TaskRepository(v10_database)
    with repo._connect() as c:
        first = c.execute("INSERT INTO projects(name) VALUES('Labor')").lastrowid
        second = c.execute("INSERT INTO projects(name) VALUES('Vertrieb')").lastrowid
    repo.save(TaskDraft(title='Laboraufgabe', project_id=first))
    other = repo.save(TaskDraft(title='Angebot', project_id=second))
    repo.save(TaskDraft(title='Unzugeordnet'))
    store = TaskStore(repo)
    shell = V10Shell(store); qtbot.addWidget(shell); shell.show(); shell.navigate(Route.TASKS)
    page = shell.page_for(Route.TASKS)
    combo = page.findChild(QComboBox, 'theme_filter')
    assert combo is not None
    titles = lambda: {r.task.title for r in page._rows}
    combo.setCurrentIndex(combo.findText('Labor'))
    assert titles() == {'Laboraufgabe'}
    shell.navigate(Route.KANBAN); shell.navigate(Route.TASKS)
    assert combo.currentText() == 'Labor'
    store.apply(SaveTask(replace(repo.get(other).draft, project_id=first), other))
    assert titles() == {'Laboraufgabe', 'Angebot'}
    combo.setCurrentIndex(combo.findText('Ohne Themengebiet'))
    assert titles() == {'Unzugeordnet'}
    combo.setCurrentIndex(combo.findText('Alle Themen'))
    assert len(titles()) == 3
    assert repo.get(other).draft.project_id == first
