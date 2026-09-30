from datetime import date

import pytest

from taskmanager.quick_capture import parse_capture
from taskmanager.task_model import ControlMode


@pytest.mark.parametrize(
    "text,expected_date",
    [
        ("Bericht heute", date(2026, 9, 23)),
        ("Bericht morgen", date(2026, 9, 24)),
        ("Bericht Freitag", date(2026, 9, 25)),
        ("Bericht nächste Woche", date(2026, 9, 28)),
    ],
)
def test_parser_recognizes_german_planning_dates(text, expected_date):
    assert parse_capture(text, date(2026, 9, 23), ()).planning_date == expected_date


@pytest.mark.parametrize("token,minutes", [("30min", 30), ("1h", 60), ("1h30", 90)])
def test_parser_recognizes_duration_formats(token, minutes):
    assert parse_capture(f"Angebot {token}", date(2026, 9, 23), ()).estimated_minutes == minutes


def test_parser_extracts_project_priority_and_control_mode():
    preview = parse_capture("Angebot Müller morgen #Vertrieb !wichtig @delegiert 30min", date(2026, 9, 23), ["Vertrieb"])
    assert preview.title == "Angebot Müller"
    assert preview.project == "Vertrieb"
    assert preview.priority == "important_not_urgent"
    assert preview.control_mode is ControlMode.DELEGATED
    assert preview.planning_date == date(2026, 9, 24)
    assert preview.estimated_minutes == 30


def test_unknown_tokens_remain_in_title():
    preview = parse_capture("Klären #Unbekannt !vielleicht bald", date(2026, 9, 23), ["Vertrieb"])
    assert preview.title == "Klären #Unbekannt !vielleicht bald"
