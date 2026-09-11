import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QFrame, QSplitter

from taskmanager.v8_detail_panel import V8DetailPanel


class WindowStub:
    def __init__(self, app):
        self._width = 1400
        self.selected_task = None
        self.editor = QFrame()
        self.editor.setMinimumWidth(320)
        self.editor.setMaximumWidth(650)
        self.left = QFrame()
        self.splitter = QSplitter()
        self.splitter.addWidget(self.left)
        self.splitter.addWidget(self.editor)
        self.splitter.resize(1000, 500)

    def width(self):
        return self._width

    def select_task(self, tid):
        self.selected_task = tid

    def resizeEvent(self, _event):
        pass


@pytest.fixture
def panel(qtbot):
    app = QApplication.instance() or QApplication([])
    window = WindowStub(app)
    qtbot.addWidget(window.splitter)
    window.splitter.show()
    return window, V8DetailPanel(window)


def test_panel_contract_starts_closed_and_default_width(panel):
    window, inspector = panel
    assert inspector.panel_open is False
    assert inspector.panel_width == 380
    assert inspector.task_id is None


def test_selection_opens_and_reopening_retains_task(panel):
    window, inspector = panel
    inspector.set_task_id(42)
    inspector.set_panel_open(True)
    assert inspector.task_id == 42
    assert inspector.panel_open is True
    inspector.set_panel_open(False)
    assert inspector.task_id == 42
    inspector.set_panel_open(True)
    assert inspector.task_id == 42
    assert inspector.panel_open is True


def test_width_is_clamped_to_practical_range(panel):
    _, inspector = panel
    inspector.set_panel_width(100)
    assert inspector.panel_width == 320
    inspector.set_panel_width(1000)
    assert inspector.panel_width == 650
    inspector.set_panel_width(440)
    assert inspector.panel_width == 440


def test_narrow_width_hides_without_clearing_selection(panel):
    window, inspector = panel
    inspector.set_task_id(7)
    inspector.set_panel_open(True)
    inspector.handle_window_width(900)
    assert inspector.panel_open is False
    assert inspector.task_id == 7
    inspector.handle_window_width(1200)
    assert inspector.panel_open is True
    assert inspector.task_id == 7
