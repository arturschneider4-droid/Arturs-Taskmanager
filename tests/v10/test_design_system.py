from taskmanager.design_tokens import Density, DesignTokens, IconRegistry, build_stylesheet


def test_design_tokens_define_professional_visual_contract():
    tokens = DesignTokens()
    assert tokens.font_family == '"Segoe UI Variable", "Segoe UI", sans-serif'
    assert tokens.accent == "#0F8F8A"
    assert tokens.navigation == "#172A3A"
    assert tokens.risk == "#C53B4B"
    assert tokens.canvas == "#F6F8FA"
    assert tokens.spacing == (4, 8, 12, 16, 24, 32)
    assert tokens.radius == (4, 8, 12)


def test_density_changes_control_and_row_heights():
    tokens = DesignTokens()
    assert tokens.metrics(Density.COMPACT).control_height == 32
    assert tokens.metrics(Density.COMFORTABLE).control_height == 40
    assert tokens.metrics(Density.COMPACT).task_row_height == 40
    assert tokens.metrics(Density.COMFORTABLE).task_row_height == 48


def test_stylesheet_covers_required_interaction_states():
    stylesheet = build_stylesheet(DesignTokens(), Density.COMPACT)
    for selector in (":hover", ":pressed", ":focus", ":disabled", '[state="loading"]', '[state="error"]'):
        assert selector in stylesheet
    assert "#0F8F8A" in stylesheet
    assert "32px" in stylesheet


def test_icon_registry_contains_every_v10_surface_icon():
    names = {
        "dashboard", "today", "inbox", "calendar", "waiting", "delegated",
        "tasks", "kanban", "eisenhower", "review", "settings", "help",
        "search", "plus", "more", "check", "bell", "person", "clock",
        "close", "chevron",
    }
    registry = IconRegistry()
    assert names <= registry.names()
    for name in names:
        assert not registry.icon(name).isNull(), name
    drawings = {(registry.icon_dir / f"{name}.svg").read_text(encoding="utf-8") for name in names}
    assert len(drawings) >= 10
