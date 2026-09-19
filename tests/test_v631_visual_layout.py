from pathlib import Path

STYLE = (Path(__file__).parents[1] / "taskmanager" / "style_v63.py").read_text(encoding="utf-8")


def test_priority_cards_have_safe_minimum_height():
    assert 'PriorityCard { min-height: 86px; }' in STYLE


def test_theme_badges_have_safe_padding_and_width():
    assert 'ThemeBadge { padding: 5px 11px; min-width: 90px; }' in STYLE


def test_date_editor_has_safe_width():
    assert 'QDateEdit { min-width: 145px; }' in STYLE
