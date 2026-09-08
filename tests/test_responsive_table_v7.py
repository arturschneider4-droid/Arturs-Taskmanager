import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "taskmanager" / "app.py"
FIX = ROOT / "taskmanager" / "responsive_table_v7.py"


def test_responsive_policy_reserves_real_layout_space():
    text = FIX.read_text(encoding="utf-8")
    assert "TASK_LEFT_MIN_WIDTH = 650" in text
    assert "EDITOR_MIN_WIDTH = 340" in text
    assert "table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)" in text
    assert "setChildrenCollapsible(False)" in text


def test_responsive_table_is_wired_after_v7_shell():
    text = APP.read_text(encoding="utf-8")
    assert "from .responsive_table_v7 import configure_responsive_task_area" in text
    assert "configure_responsive_task_area(w)" in text
    assert text.index("rebuild_professional_shell(w)") < text.index("configure_responsive_task_area(w)")


def test_qt_geometry_keeps_task_table_and_editor_inside_window(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from taskmanager.db import init_db
    from taskmanager.ui import MainWindow
    from taskmanager.style_v7 import rebuild_professional_shell
    from taskmanager.responsive_table_v7 import configure_responsive_task_area

    app = QApplication.instance() or QApplication([])
    init_db()
    window = MainWindow()
    rebuild_professional_shell(window)
    configure_responsive_task_area(window)
    window.resize(1280, 760)
    window.show()
    app.processEvents()

    assert window.width() >= 1280
    splitter = window.editor.parentWidget()
    sizes = splitter.sizes()
    assert sizes[0] >= 650
    assert sizes[1] >= 340
    assert window.table.width() >= 650 - 30
    assert window.table.horizontalScrollBarPolicy().name == "ScrollBarAlwaysOff"

    window.close()
    app.processEvents()
