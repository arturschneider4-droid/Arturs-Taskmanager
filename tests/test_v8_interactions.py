from datetime import date

from taskmanager.v8_interactions import (
    format_due_date,
    next_planning_due,
    priority_label,
    responsive_layout,
    scope_for_view,
)


def test_due_labels_are_semantic():
    today = date(2026, 9, 11)
    assert format_due_date("2026-09-11", today) == "Heute"
    assert format_due_date("2026-09-12", today) == "Morgen"
    assert format_due_date("2026-09-10", today) == "Überfällig"
    assert format_due_date(None, today) == "Keine Fälligkeit"
    assert format_due_date("2026-09-20", today) == "20.09.2026"


def test_priority_labels_are_complete():
    assert priority_label("important_urgent") == "Wichtig & dringend"
    assert priority_label("important_not_urgent") == "Wichtig & nicht dringend"
    assert priority_label("not_important_urgent") == "Nicht wichtig & dringend"
    assert priority_label("not_important_not_urgent") == "Nicht wichtig & nicht dringend"


def test_supported_views_map_to_existing_scopes():
    assert scope_for_view("tasks") == ("Alle Aufgaben", "Alle")
    assert scope_for_view("today") == ("Heute", "Heute")
    assert scope_for_view("week") == ("Diese Woche", "Diese Woche")
    assert scope_for_view("later") == ("Später", "Später")
    assert scope_for_view("done") == ("Erledigt", "Erledigt")


def test_responsive_layout_hides_detail_before_workspace_becomes_unusable():
    assert responsive_layout(1500, True, False)["detail_visible"] is True
    assert responsive_layout(1100, True, False)["detail_visible"] is True
    narrow = responsive_layout(900, True, False)
    assert narrow["detail_visible"] is False
    assert narrow["nav_collapsed"] is True
    assert responsive_layout(1500, False, False)["detail_visible"] is False


def test_planning_targets_have_named_period_dates():
    today = date(2026, 9, 11)  # Friday
    assert next_planning_due("Heute", today) == "2026-09-11"
    assert next_planning_due("Diese Woche", today) == "2026-09-13"
    assert next_planning_due("Später", today) == "2026-09-14"
