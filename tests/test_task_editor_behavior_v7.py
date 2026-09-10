import os


def test_editor_subtask_buttons_follow_selection_and_edit_selected_item(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QListWidgetItem, QPushButton, QInputDialog

    from taskmanager.ui import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        edit = next(
            b for b in window.editor.findChildren(QPushButton)
            if b.text() == "Bearbeiten"
        )
        remove = next(
            b for b in window.editor.findChildren(QPushButton)
            if b.text() == "Löschen"
        )
        item = QListWidgetItem("Alt")
        window.e_subs.addItem(item)

        window.e_subs.clearSelection()
        app.processEvents()
        assert not edit.isEnabled()
        assert not remove.isEnabled()

        window.e_subs.setCurrentItem(item)
        app.processEvents()
        assert edit.isEnabled()
        assert remove.isEnabled()

        monkeypatch.setattr(
            QInputDialog,
            "getText",
            staticmethod(lambda *args, **kwargs: ("Neu", True)),
        )
        edit.click()
        app.processEvents()
        assert item.text() == "Neu"
    finally:
        window.close()
