from datetime import date
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLabel
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore, SaveTask
from taskmanager.v10_shell import V10Shell
from taskmanager.navigation import Route
from taskmanager.design_tokens import DesignTokens, Density, build_stylesheet

@pytest.mark.parametrize('density', list(Density))
def test_crowded_task_rows_keep_title_dates_and_actions_separate(qtbot, v10_database, density):
    repo=TaskRepository(v10_database)
    for i in range(25): repo.save(TaskDraft(title=f'Angebotsvorlage prüfen {i}', deadline=date(2026,10,2)))
    shell=V10Shell(TaskStore(repo));qtbot.addWidget(shell);shell.resize(1366,768)
    shell.setStyleSheet(build_stylesheet(DesignTokens(),density))
    shell.navigate(Route.TASKS);shell.show();qtbot.wait(30)
    rows=shell.page_for(Route.TASKS)._rows
    for row in rows:
        title=row.title_button.geometry(); dates=row.planning_label.geometry()
        assert title.bottom() < dates.top(), (title,dates,row.height())
        assert row.rect().contains(dates)
        for button in row.buttons.values():
            if button.isVisible():
                assert title.bottom() < button.geometry().top()
                assert row.rect().contains(button.geometry())
    assert all(a.geometry().bottom()<b.geometry().top() for a,b in zip(rows,rows[1:]))


def test_focus_can_collapse_expand_and_stay_collapsed_after_details_and_restart(qtbot,v10_database):
    repo=TaskRepository(v10_database);task=repo.save(TaskDraft(title='Aufgabe'))
    shell=V10Shell(TaskStore(repo));qtbot.addWidget(shell);shell.resize(1366,768);shell.show();qtbot.wait(20)
    button=shell.findChild(QPushButton,'toggle_weekly_focus')
    assert button is not None, 'Wochenfokus benötigt einen sichtbaren Schalter'
    before=shell.center.width();button.click();qtbot.wait(20)
    assert not shell.context_stack.isVisible()
    assert shell.center.width()>before
    shell.detail_panel.open_task(task);assert shell.detail_panel.isVisible()
    shell.detail_panel.close_button.click();assert not shell.context_stack.isVisible()
    shell.close()
    second=V10Shell(TaskStore(repo));qtbot.addWidget(second);second.resize(1366,768);second.show()
    assert not second.context_stack.isVisible()
    second.findChild(QPushButton,'toggle_weekly_focus').click()
    assert second.weekly_focus.isVisible()
    second.resize(720,640);qtbot.wait(20)
    second.findChild(QPushButton,'toggle_weekly_focus').click()
    assert second.weekly_focus.isVisible()
    collapse=second.weekly_focus.findChild(QPushButton,'collapse_weekly_focus')
    assert collapse is not None
    collapse.click();assert second.center.isVisible()


def test_kanban_card_shows_deadline_and_distinct_eisenhower_categories(qtbot,v10_database):
    repo=TaskRepository(v10_database)
    priorities=('important_urgent','important_not_urgent','not_important_urgent','not_important_not_urgent')
    for i,p in enumerate(priorities):repo.save(TaskDraft(title=f'Karte {i}',priority=p,deadline=date(2026,10,8) if i else None))
    shell=V10Shell(TaskStore(repo));qtbot.addWidget(shell);shell.resize(1366,768);shell.navigate(Route.KANBAN);shell.show();qtbot.wait(20)
    board=shell.page_for(Route.KANBAN);lane=board.lane_widgets['Offen'];colors=set()
    for i in range(lane.count()):
        item=lane.item(i);card=lane.itemWidget(item)
        assert card is not None, 'Karte benötigt sichtbare Deadline und Kategorie'
        labels=card.findChildren(QLabel)
        text=' '.join(label.text() for label in labels)
        assert ('Keine Deadline' if item.text().startswith('Karte 0') else '08.10.2026') in text
        badge=card.findChild(QLabel,'kanban_priority')
        assert badge is not None and badge.text()
        colors.add(badge.styleSheet())
    assert len(colors)==4

@pytest.mark.parametrize('width', [720, 1366, 1920])
def test_long_kanban_titles_are_fully_visible(qtbot, v10_database, width):
    repo = TaskRepository(v10_database)
    repo.save(TaskDraft(title='Rahmenangebot für strategischen Kunden finalisieren und mit der Laborleitung verbindlich abstimmen', deadline=date(2026,10,8)))
    shell = V10Shell(TaskStore(repo)); qtbot.addWidget(shell)
    shell.resize(width, 768); shell.navigate(Route.KANBAN); shell.show(); qtbot.wait(30)
    lane = shell.page_for(Route.KANBAN).lane_widgets['Offen']
    card = lane.itemWidget(lane.item(0))
    for label in card.findChildren(QLabel):
        assert label.height() >= label.heightForWidth(label.width()), (label.text(), label.size(), label.heightForWidth(label.width()))

@pytest.mark.parametrize("theme", [None, "Vertrieb", "Langfristige strategische Geschäftsentwicklung und Kundenbetreuung"])
def test_kanban_card_displays_theme(qtbot, theme):
    from types import SimpleNamespace
    from taskmanager.board_views import KanbanCard
    task = SimpleNamespace(title="Aufgabe", project_name=theme, priority="important_urgent", is_top_three=False, deadline=None, status="Offen")
    card = KanbanCard(task); qtbot.addWidget(card); card.resize(200, 320); card.show()
    label = card.findChild(QLabel, "kanban_theme")
    assert label is not None
    assert label.text() == (theme or "Ohne Themengebiet")
    assert label.wordWrap()
    assert label.text() in card.accessibleName()

@pytest.mark.parametrize("offset,status,archived,warning", [(-1,"Offen",False,True),(-1,"In Arbeit",False,True),(0,"Offen",False,False),(1,"Offen",False,False),(None,"Offen",False,False),(-1,"Erledigt",False,False),(-1,"Erledigt",True,False)])
def test_kanban_overdue_deadline_warning(qtbot, offset, status, archived, warning):
    from types import SimpleNamespace
    from datetime import timedelta
    from taskmanager.board_views import KanbanCard
    task = SimpleNamespace(title="Frist prüfen", project_name="Labor", priority="important_urgent", is_top_three=False, deadline=date.today()+timedelta(days=offset) if offset is not None else None, status=status, archived_at=date.today() if archived else None)
    card = KanbanCard(task); qtbot.addWidget(card); card.show()
    icon = card.findChild(QLabel, "kanban_overdue_warning")
    assert (icon is not None) == warning
    assert ("überfällig" in card.deadline_label.text()) == warning
    if warning:
        assert icon.text() == "!"
        assert "#A3293D" in icon.styleSheet()
        assert icon.accessibleName() == "Deadline überschritten"
