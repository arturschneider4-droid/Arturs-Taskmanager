import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_qfont_is_imported_from_qtgui():
    """QFont belongs to QtGui; importing it from QtWidgets breaks the frozen EXE."""
    tree = ast.parse((ROOT / "taskmanager" / "priority_sync.py").read_text(encoding="utf-8"))

    imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "PySide6.QtWidgets"
        for alias in node.names
    }
    qtgui_imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "PySide6.QtGui"
        for alias in node.names
    }

    assert "QFont" not in imports
    assert "QFont" in qtgui_imports
