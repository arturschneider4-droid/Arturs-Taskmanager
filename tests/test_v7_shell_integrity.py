import gc
import os


def test_v7_shell_keeps_legacy_refresh_dependencies_alive():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from taskmanager.db import init_db
    from taskmanager.ui import MainWindow
    from taskmanager.style_v7 import rebuild_professional_shell

    app = QApplication.instance() or QApplication([])
    init_db()
    window = MainWindow()
    rebuild_professional_shell(window)
    gc.collect()
    app.processEvents()

    # refresh_all is part of the normal post-edit/post-filter path and must
    # remain safe after the V7 shell replaces the legacy central widget.
    window.refresh_all()
    assert window.projects is not None
    assert window.stack is not None
    window.close()


def test_v7_themes_navigation_and_task_navigation_share_one_stack():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from taskmanager.db import init_db
    from taskmanager.ui import MainWindow
    from taskmanager.style_v7 import rebuild_professional_shell

    app = QApplication.instance() or QApplication([])
    init_db()
    window = MainWindow()
    rebuild_professional_shell(window)

    window.set_view("themes")
    assert window.stack.currentWidget().objectName() == "v7ThemesWorkspace"
    window.set_view("tasks")
    assert window.stack.currentWidget() is window.tasks_page
    window.set_view("kanban")
    assert window.stack.currentWidget() is window.kanban
    window.set_view("eisenhower")
    assert window.stack.currentWidget() is window.eisen
    window.set_view("planning")
    assert window.stack.currentWidget() is window.plan
    window.close()
