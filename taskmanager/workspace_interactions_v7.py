"""V7 workspace interaction fixes that are independent of the visual shell."""

from datetime import date, timedelta

from .db import task, update_due, update_priority
from .constants import PRIORITIES, STATUS


def apply_workspace_interaction_fixes(window):
    """Install the corrected Planning drag/drop semantics once."""
    if getattr(window, "_v7_workspace_interactions_installed", False):
        return

    original = window.drop_moved

    def drop_moved(tid, target):
        if target in STATUS or target in PRIORITIES:
            return original(tid, target)
        if not task(tid):
            return
        today = date.today()
        week_end = today + timedelta(days=6 - today.weekday())
        if target == "Heute":
            due = today
        elif target == "Diese Woche":
            due = week_end
        elif target == "Später":
            due = week_end + timedelta(days=1)
        else:
            return original(tid, target)
        update_due(tid, due.isoformat())
        window.refresh_all()
        window._set_undo_available()

    window.drop_moved = drop_moved
    window._v7_workspace_interactions_installed = True
