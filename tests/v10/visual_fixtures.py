from contextlib import ExitStack
from datetime import date
from pathlib import Path
import tempfile
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from taskmanager import db
from taskmanager.migrations import migrate_to_v10
from taskmanager.navigation import Route
from taskmanager.repositories import TaskRepository
from taskmanager.task_model import TaskDraft
from taskmanager.task_store import TaskStore
from taskmanager.v10_shell import V10Shell

SIZES = ((1920, 1080), (1366, 768), (720, 640))
ROUTES = tuple(Route)

class VisualDate(date):
    @classmethod
    def today(cls): return cls(2026, 9, 30)


def baseline_name(route, size):
    return f"{route.value}-{size[0]}x{size[1]}.png"


def seed_visual_tasks(repository):
    examples = (
        TaskDraft(title="Prüfbericht mit Laborleitung freigeben", status="In Arbeit", planning_date=date(2026,9,30), deadline=date(2026,10,2), is_top_three=True),
        TaskDraft(title="Rahmenangebot für strategischen Kunden finalisieren", priority="important_urgent", planning_date=date(2026,9,30), deadline=date(2026,9,29)),
        TaskDraft(title="Rückmeldung zur Prüfplanung einholen", control_mode="waiting", responsible_party="Projektteam", follow_up_date=date(2026,9,30)),
        TaskDraft(title="Kapazitätsplanung für das nächste Quartal abstimmen", control_mode="delegated", responsible_party="Laborleitung", follow_up_date=date(2026,10,2), planning_date=date(2026,10,2)),
        TaskDraft(title="Neue Anfrage sichten und Anforderungen klären"),
        TaskDraft(title="Teamgespräche vorbereiten", planning_date=date(2026,10,1), priority="not_important_urgent"),
        TaskDraft(title="Monatsabschluss dokumentiert", status="Erledigt", planning_date=date(2026,9,29), priority="not_important_not_urgent"),
    )
    for item in examples: repository.save(item)
    c=repository._connect();c.execute("UPDATE tasks SET created_at='2026-09-28T09:00:00', updated_at='2026-09-30T09:00:00'");c.commit();c.close()


def render_route(route: Route, size: tuple[int, int], target: Path):
    # Freeze application clocks; reference images must remain valid next week.
    from taskmanager import dashboard, repositories, follow_up, task_list, calendar_view, weekly_review, quick_capture, detail_panel, board_views
    with tempfile.TemporaryDirectory(prefix="v10-visual-") as directory, ExitStack() as patches:
        for module in (dashboard,repositories,follow_up,task_list,calendar_view,weekly_review,quick_capture,detail_panel,board_views):
            patches.enter_context(patch.object(module, 'date', VisualDate))
        db.configure_storage(Path(directory)); db.init_db(); migrate_to_v10(db.DB_PATH, db.BACKUP_DIR)
        repo=TaskRepository(db.DB_PATH);seed_visual_tasks(repo)
        shell = V10Shell(TaskStore(repo))
        shell.resize(*size); shell.navigate(route); shell.show()
        QApplication.processEvents(); QApplication.processEvents()
        target.parent.mkdir(parents=True, exist_ok=True)
        assert shell.grab().save(str(target))
        shell.close();shell.deleteLater();QApplication.processEvents()
    return target
