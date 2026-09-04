from datetime import date, timedelta

from taskmanager.overview import overview_scope, overview_counts


def test_overview_scope_maps_each_item_to_filters():
    assert overview_scope("Heute") == {"due": "Heute", "status": None}
    assert overview_scope("Diese Woche") == {"due": "Diese Woche", "status": None}
    assert overview_scope("Später") == {"due": "Später", "status": None}
    assert overview_scope("Erledigt") == {"due": "Alle Fälligkeiten", "status": "Erledigt"}
    assert overview_scope("Alle") == {"due": "Alle Fälligkeiten", "status": "Alle Status"}


def test_overview_counts_categories_are_consistent():
    # Use a fixed Wednesday so the relative test data remains inside the
    # same calendar week regardless of the day the CI job runs.
    today = date(2026, 9, 2)
    week_end = today + timedelta(days=6 - today.weekday())
    rows = [
        {"status": "Offen", "due_date": today.isoformat()},
        {"status": "In Arbeit", "due_date": (today + timedelta(days=2)).isoformat()},
        {"status": "Erledigt", "due_date": (today + timedelta(days=3)).isoformat()},
        {"status": "Offen", "due_date": (week_end + timedelta(days=1)).isoformat()},
        {"status": "Offen", "due_date": None},
    ]

    counts = overview_counts(rows, today=today)

    assert counts == {"Heute": 1, "Diese Woche": 2, "Später": 2, "Erledigt": 1, "Alle": 5}
