from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PySide6.QtGui import QIcon


class Density(str, Enum):
    COMPACT = "compact"
    COMFORTABLE = "comfortable"


@dataclass(frozen=True)
class DensityMetrics:
    control_height: int
    task_row_height: int
    horizontal_padding: int


@dataclass(frozen=True)
class DesignTokens:
    font_family: str = '"Segoe UI Variable", "Segoe UI", sans-serif'
    navigation: str = "#172A3A"
    navigation_hover: str = "#203A4D"
    canvas: str = "#F6F8FA"
    surface: str = "#FFFFFF"
    text: str = "#17212B"
    text_muted: str = "#687683"
    border: str = "#DDE4E9"
    accent: str = "#0F8F8A"
    accent_hover: str = "#0B7773"
    success: str = "#27845A"
    warning: str = "#B97817"
    risk: str = "#C53B4B"
    spacing: tuple[int, ...] = (4, 8, 12, 16, 24, 32)
    radius: tuple[int, ...] = (4, 8, 12)

    def metrics(self, density: Density) -> DensityMetrics:
        if Density(density) is Density.COMPACT:
            return DensityMetrics(32, 40, 12)
        return DensityMetrics(40, 48, 16)


def build_stylesheet(tokens: DesignTokens, density: Density) -> str:
    metrics = tokens.metrics(density)
    return f"""
    QWidget {{ font-family: {tokens.font_family}; color: {tokens.text}; font-size: 13px; }}
    QMainWindow, QWidget#v10Root, QStackedWidget#v10Pages {{ background: {tokens.canvas}; }}
    QWidget#v10Navigation {{ background: {tokens.navigation}; border: none; }}
    QWidget#v10Navigation QPushButton {{ color: #DCE7ED; background: transparent; border: 0; border-radius: 8px; text-align: left; padding-left: 14px; font-weight: 500; }}
    QWidget#v10Navigation QPushButton:hover {{ color: white; background: {tokens.navigation_hover}; }}
    QWidget#v10Navigation QPushButton[active="true"] {{ color: white; background: {tokens.accent}; font-weight: 700; }}
    QStackedWidget#v10Context, QWidget#weeklyFocusPanel, QFrame#v10DetailPanel {{ background: {tokens.surface}; border-left: 1px solid {tokens.border}; }}
    QWidget#weeklyFocusPanel {{ padding: 18px; }}
    QLabel#pageTitle {{ font-size: 26px; font-weight: 700; color: {tokens.navigation}; padding: 8px 0 12px 0; }}
    QPushButton {{ min-height: {metrics.control_height}px; padding: 0 {metrics.horizontal_padding}px; border: 1px solid {tokens.border}; border-radius: {tokens.radius[1]}px; background: {tokens.surface}; }}
    QPushButton:hover {{ border-color: {tokens.accent}; background: #F0FAF9; }}
    QPushButton:pressed {{ background: #DDF3F1; }}
    QPushButton:focus {{ border: 2px solid {tokens.accent}; }}
    QPushButton:disabled {{ color: #9AA6AF; background: #F0F2F4; }}
    QPushButton[variant="primary"] {{ color: white; background: {tokens.accent}; border-color: {tokens.accent}; font-weight: 600; }}
    QPushButton[variant="primary"]:hover {{ background: {tokens.accent_hover}; }}
    QWidget[state="loading"] {{ color: {tokens.text_muted}; }}
    QWidget[state="error"] {{ color: {tokens.risk}; border-color: {tokens.risk}; }}
    QWidget[role="task-row"] {{ min-height: {metrics.task_row_height}px; background: {tokens.surface}; border-bottom: 1px solid {tokens.border}; }}
    QPushButton[role="metric-card"] {{ min-height: 108px; text-align: left; background: {tokens.surface}; border: 1px solid {tokens.border}; border-radius: 12px; }}
    QPushButton[role="metric-card"]:hover {{ border: 1px solid {tokens.accent}; background: #F3FBFA; }}
    QLabel#metricValue {{ font-size: 28px; font-weight: 700; color: {tokens.navigation}; }}
    QLabel#laneTitle {{ font-size: 15px; font-weight: 600; padding: 8px 0; }}
    QLabel#emptyState {{ color: {tokens.text_muted}; padding: 24px; }}
    QFrame#quickCaptureOverlay, QFrame#commandSearchOverlay {{ background: white; border: 2px solid {tokens.accent}; border-radius: 12px; padding: 12px; }}
    QListWidget#boardLane {{ background: #EEF3F6; padding: 8px; border-top: 3px solid {tokens.accent}; }}
    QListWidget#boardLane::item {{ background: white; border: 1px solid {tokens.border}; border-radius: 8px; padding: 10px; }}
    QListWidget#boardLane::item:selected {{ background: #DDF3F1; border-color: {tokens.accent}; color: {tokens.text}; }}
    QToolButton {{ padding: 5px 8px; border: 1px solid {tokens.border}; border-radius: 5px; background: white; }}
    QToolButton:hover {{ background: #DDF3F1; }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit, QDateTimeEdit {{ min-height: {metrics.control_height}px; background: white; border: 1px solid {tokens.border}; border-radius: 7px; padding: 0 10px; selection-background-color: {tokens.accent}; }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{ border: 2px solid {tokens.accent}; }}
    QScrollArea, QListWidget, QTreeWidget {{ background: {tokens.surface}; border: 1px solid {tokens.border}; border-radius: 8px; }}
    QHeaderView::section {{ background: #EDF2F5; color: {tokens.text_muted}; border: 0; border-bottom: 1px solid {tokens.border}; padding: 9px; font-weight: 600; }}
    QWidget[role="chip"] {{ border-radius: {tokens.radius[0]}px; background: #EAF4F4; color: #116B68; padding: 4px 8px; }}
    """


class IconRegistry:
    REQUIRED = {
        "dashboard", "today", "inbox", "calendar", "waiting", "delegated",
        "tasks", "kanban", "eisenhower", "review", "settings", "help",
        "search", "plus", "more", "check", "bell", "person", "clock",
        "close", "chevron",
    }

    def __init__(self, icon_dir: Path | None = None):
        self.icon_dir = icon_dir or Path(__file__).parent / "assets" / "icons"

    def names(self) -> set[str]:
        return {path.stem for path in self.icon_dir.glob("*.svg")}

    def icon(self, name: str) -> QIcon:
        if name not in self.REQUIRED:
            raise KeyError(name)
        return QIcon(str(self.icon_dir / f"{name}.svg"))
