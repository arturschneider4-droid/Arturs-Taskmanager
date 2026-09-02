from datetime import date, datetime, timedelta

from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFrame, QLabel


def overview_scope(label):
    mapping = {
        "Heute": {"due": "Heute", "status": None},
        "Diese Woche": {"due": "Diese Woche", "status": None},
        "Später": {"due": "Später", "status": None},
        "Erledigt": {"due": "Alle Fälligkeiten", "status": "Erledigt"},
        "Alle": {"due": "Alle Fälligkeiten", "status": "Alle Status"},
    }
    return dict(mapping[label])


def overview_counts(rows, today=None):
    today = today or date.today()
    week_end = today + timedelta(days=6 - today.weekday())
    counts = {"Heute": 0, "Diese Woche": 0, "Später": 0, "Erledigt": 0, "Alle": len(rows)}
    for row in rows:
        if row["status"] == "Erledigt":
            counts["Erledigt"] += 1
        due = row.get("due_date")
        if not due:
            counts["Später"] += 1
            continue
        task_date = datetime.strptime(due, "%Y-%m-%d").date()
        if task_date == today:
            counts["Heute"] += 1
        elif task_date <= week_end:
            counts["Diese Woche"] += 1
        else:
            counts["Später"] += 1
    return counts


class _OverviewClickFilter(QObject):
    """Click filter with no QObject parent for PySide6/PyInstaller compatibility."""
    def __init__(self, window, label, key):
        super().__init__()
        self.window = window
        self.label = label
        self.key = key
        label.setCursor(QCursor(Qt.PointingHandCursor))
        label.setToolTip(f"{label.text()} anzeigen")
        label.setProperty("overviewClickable", True)

    def eventFilter(self, obj, event):
        if obj is self.label and event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.window.set_overview_scope(self.key)
            return True
        return False


def install_overview_navigation(window):
    overview = window.findChild(QFrame, "overview")
    if overview is None:
        return False

    labels = {}
    for label in overview.findChildren(QLabel):
        text = label.text().strip()
        if text in {"Heute", "Diese Woche", "Später", "Erledigt", "Alle Aufgaben"}:
            labels[text] = label

    if not hasattr(window, "_overview_filters"):
        window._overview_filters = []

    for text, label in labels.items():
        key = "Alle" if text == "Alle Aufgaben" else text
        filt = _OverviewClickFilter(window, label, key)
        label.installEventFilter(filt)
        window._overview_filters.append(filt)

    window.set_overview_scope = lambda key: _apply_scope(window, key)
    return len(labels) == 5


def _apply_scope(window, key):
    filters = overview_scope(key)
    if filters["status"] is None:
        window.sfilter.setCurrentText("Alle Status")
    else:
        window.sfilter.setCurrentText(filters["status"])
    window.dfilter.setCurrentText(filters["due"])
    window.scope = key
    if hasattr(window, "scope_buttons"):
        for name, button in window.scope_buttons.items():
            active = name == key
            button.setProperty("active", str(active).lower())
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
    window.refresh_all()
