import os


def test_task_checkbox_click_changes_status():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt, QObject
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QCheckBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QWidget
    from taskmanager.responsive_table_v7 import _TaskAreaController, _install_task_checkbox_controller

    app = QApplication.instance() or QApplication([])

    window = QObject()
    calls = []
    window.set_status = lambda tid, status: calls.append((tid, status))

    table = QTableWidget(1, 2)
    item = QTableWidgetItem("Aufgabe")
    item.setData(Qt.UserRole, 123)
    table.setItem(0, 1, item)

    cell = QWidget()
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(0, 0, 0, 0)
    checkbox = QCheckBox(cell)
    checkbox.setChecked(False)
    layout.addWidget(checkbox)
    table.setCellWidget(0, 0, cell)

    controller = _TaskAreaController(window, table, None)
    _install_task_checkbox_controller(controller)
    table.show()
    app.processEvents()

    QTest.mouseClick(cell, Qt.LeftButton, pos=cell.rect().center())
    app.processEvents()
    assert calls[-1] == (123, "Erledigt")

    checkbox.setChecked(True)
    QTest.mouseClick(cell, Qt.LeftButton, pos=cell.rect().center())
    app.processEvents()
    assert calls[-1] == (123, "Offen")
