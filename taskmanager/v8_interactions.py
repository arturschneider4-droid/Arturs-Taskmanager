from datetime import date, timedelta

from PySide6.QtWidgets import QListWidget

from .constants import PRIORITIES


def format_due_date(value, today=None):
    if not value:
        return "Keine Fälligkeit"
    today = today or date.today()
    due = date.fromisoformat(value) if isinstance(value, str) else value
    if due == today:
        return "Heute"
    if due == today + timedelta(days=1):
        return "Morgen"
    if due < today:
        return "Überfällig"
    return due.strftime("%d.%m.%Y")


def priority_label(priority):
    return PRIORITIES.get(priority, "Unbekannte Priorität")


def scope_for_view(view_key):
    mapping = {
        "tasks": ("Alle Aufgaben", "Alle"),
        "today": ("Heute", "Heute"),
        "week": ("Diese Woche", "Diese Woche"),
        "later": ("Später", "Später"),
        "done": ("Erledigt", "Erledigt"),
    }
    return mapping.get(view_key, ("Alle Aufgaben", "Alle"))


def responsive_layout(width, detail_open, nav_collapsed):
    # Detail is removed before the workspace becomes too narrow; navigation
    # follows at the compact breakpoint.
    if width < 1200:
        return {"detail_visible": False, "nav_collapsed": True}
    return {
        "detail_visible": bool(detail_open),
        "nav_collapsed": bool(nav_collapsed),
    }


def next_planning_due(target, today=None):
    today = today or date.today()
    week_end = today + timedelta(days=6 - today.weekday())
    if target == "Heute":
        return today.isoformat()
    if target == "Diese Woche":
        return week_end.isoformat()
    if target == "Später":
        return (week_end + timedelta(days=1)).isoformat()
    raise ValueError(f"Unknown planning target: {target}")


def drop_event_was_accepted(event):
    """Return whether Qt accepted the drop, without relying on target mode."""
    checker = getattr(event, "isAccepted", None)
    return bool(checker()) if callable(checker) else False


def install_drop_guard(_window=None):
    """Make DropList emit its persistence signal only for accepted drops."""
    from .ui import DropList

    if getattr(DropList, "_v8_drop_guard_installed", False):
        return

    def guarded_drop_event(self, event):
        drag_id = self.drag_id
        QListWidget.dropEvent(self, event)
        if drag_id is not None and drop_event_was_accepted(event):
            self.moved.emit(drag_id, self.mode)
        self.drag_id = None

    DropList.dropEvent = guarded_drop_event
    DropList._v8_drop_guard_installed = True
