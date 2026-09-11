from datetime import date, timedelta

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
    if width < 960:
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
