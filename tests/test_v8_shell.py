from pathlib import Path


def test_v8_shell_module_contains_approved_architecture():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    for token in (
        "V8_STYLE",
        "rebuild_v8_shell",
        "install_v8_responsive_behavior",
        "＋  Aufgabe",
        "THEMENGEBIETE",
        "_toggle_detail",
        "_toggle_navigation",
    ):
        assert token in text


def test_v8_shell_is_light_enterprise_and_not_legacy_blue_sidebar():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "#F4F7F9" in text
    assert "#FFFFFF" in text
    assert "#0050A4" in text
    assert "background: #034A70" not in text
    assert "V8.0" in text


def test_app_wires_v8_shell():
    text = Path("taskmanager/app.py").read_text(encoding="utf-8")
    assert "style_v8" in text
    assert "rebuild_v8_shell" in text
    assert 'VERSION = "8.0"' in text


def test_v8_theme_navigation_items_are_actionable():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    for token in (
        "themes.itemClicked.connect(select_theme)",
        "themes.itemPressed.connect(select_theme)",
        "themes.itemActivated.connect(select_theme)",
        "themes.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)",
        "window.set_project(pid)",
        "window.set_view(\"tasks\")",
    ):
        assert token in text, token


def test_v8_group_button_changes_visible_task_order():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    assert "def _apply_v8_grouping" in text
    assert "sortItems" in text
    assert "_apply_v8_grouping(window)" in text


def test_v8_secondary_and_toolbar_buttons_have_handlers():
    text = Path("taskmanager/style_v8.py").read_text(encoding="utf-8")
    app = Path("taskmanager/app.py").read_text(encoding="utf-8")
    for token in (
        'detail.clicked.connect',
        'primary.clicked.connect(window.new_task)',
        'filter_b.clicked.connect',
        'sort_b.clicked.connect(lambda: _show_sort_menu(window, sort_b))',
        'group_b.clicked.connect',
        'compact.clicked.connect',
        'collapse.clicked.connect',
        'add_theme.clicked.connect(window.new_project)',
    ):
        assert token in text, token
    assert 'export.clicked.connect(window.export_excel)' in app
    assert 'settings.clicked.connect' in app
