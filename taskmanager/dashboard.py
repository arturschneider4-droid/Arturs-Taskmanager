from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
import sqlite3

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QCheckBox, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .components import MetricCard, PrimaryButton
from .repositories import DashboardRepository
from .task_store import ChangeSet, TaskStore


class DashboardFilter(str, Enum):
    TODAY = "today"
    OVERDUE = "overdue"
    FOLLOW_UPS = "follow_ups"
    DELEGATED = "delegated"
    TOP_THREE = "top_three"
    CRITICAL_DEADLINES = "critical_deadlines"
    UNPLANNED = "unplanned"
    WEEK_PROGRESS = "week_progress"

    @property
    def label(self) -> str:
        return {
            self.TODAY: "Heute offen", self.OVERDUE: "Überfällig",
            self.FOLLOW_UPS: "Fällige Wiedervorlagen", self.DELEGATED: "Offene Delegationen",
            self.TOP_THREE: "Top 3 des Tages", self.CRITICAL_DEADLINES: "Kritische Deadlines",
            self.UNPLANNED: "Ohne Planung", self.WEEK_PROGRESS: "Wochenfortschritt",
        }[self]


@dataclass(frozen=True)
class DashboardSnapshot:
    metric_values: dict[str, int]


@dataclass(frozen=True)
class WeeklyGoal:
    title: str
    done: bool


@dataclass(frozen=True)
class WeeklyFocusSnapshot:
    goals: tuple[WeeklyGoal, ...]
    next_deadline: str | None
    oldest_delegation: str | None
    next_follow_up: str | None
    progress_percent: int


class DashboardService:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def snapshot(self, today: date) -> DashboardSnapshot:
        metrics = DashboardRepository(self.db_path).metrics(today)
        total_week = metrics.completed_this_week + metrics.today_open + metrics.unplanned
        progress = round(metrics.completed_this_week * 100 / total_week) if total_week else 0
        return DashboardSnapshot({
            "today": metrics.today_open, "overdue": metrics.overdue,
            "follow_ups": metrics.due_follow_ups, "delegated": metrics.delegated_open,
            "top_three": metrics.top_three, "critical_deadlines": metrics.critical_next_seven_days,
            "unplanned": metrics.unplanned, "week_progress": progress,
        })

    def weekly_focus(self, today: date) -> WeeklyFocusSnapshot:
        year, week, _ = today.isocalendar()
        connection = sqlite3.connect(self.db_path)
        goals = tuple(WeeklyGoal(row[0], bool(row[1])) for row in connection.execute(
            "SELECT title,done FROM weekly_goals WHERE year=? AND week=? ORDER BY position LIMIT 3", (year, week)
        ))
        deadline = connection.execute("SELECT title FROM tasks WHERE status!='Erledigt' AND deadline>=? ORDER BY deadline,id LIMIT 1", (today.isoformat(),)).fetchone()
        delegation = connection.execute("SELECT title FROM tasks WHERE status!='Erledigt' AND control_mode='delegated' ORDER BY delegated_at,id LIMIT 1").fetchone()
        follow_up = connection.execute("SELECT title FROM tasks WHERE status!='Erledigt' AND follow_up_date IS NOT NULL ORDER BY follow_up_date,id LIMIT 1").fetchone()
        connection.close()
        progress = round(sum(goal.done for goal in goals) * 100 / len(goals)) if goals else 0
        return WeeklyFocusSnapshot(goals, deadline[0] if deadline else None, delegation[0] if delegation else None, follow_up[0] if follow_up else None, progress)


class ExecutiveDashboard(QWidget):
    filter_requested = Signal(object)

    def __init__(self, store: TaskStore, today: date | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("executiveDashboard")
        self.store = store
        self.today = today or date.today()
        self.service = DashboardService(store.repository.db_path)
        self.refresh_count = 0
        self._cards = {}
        layout = QVBoxLayout(self)
        title = QLabel("Executive Dashboard")
        title.setObjectName("pageTitle")
        title.hide() # The shell provides the page heading
        grid = QGridLayout(); self.grid = grid
        for index, filter_key in enumerate(DashboardFilter):
            card = MetricCard(filter_key.label, 0, filter_key.value)
            card.setObjectName(f"metric_{filter_key.value}")
            card.activated.connect(lambda _key, value=filter_key: self.filter_requested.emit(value))
            self._cards[filter_key] = card
            grid.addWidget(card, index // 4, index % 4)
        layout.addLayout(grid)
        layout.addStretch(1)
        store.changed.connect(self._on_change)
        self.refresh()

    def resizeEvent(self, event):
        columns = 4 if event.size().width() >= 1000 else 2
        for index, card in enumerate(self._cards.values()):
            self.grid.removeWidget(card); self.grid.addWidget(card, index // columns, index % columns)
        super().resizeEvent(event)

    def card_for(self, filter_key: DashboardFilter) -> MetricCard:
        return self._cards[filter_key]

    def refresh(self) -> None:
        snapshot = self.service.snapshot(self.today)
        for filter_key, card in self._cards.items():
            value = snapshot.metric_values[filter_key.value]
            card.value_label.setText(f"{value} %" if filter_key is DashboardFilter.WEEK_PROGRESS else str(value))
            card.setAccessibleName(f"{filter_key.label}: {value}")
        self.refresh_count += 1

    def _on_change(self, change: ChangeSet) -> None:
        if "dashboard" in change.domains:
            self.refresh()


class WeeklyFocusPanel(QWidget):
    review_requested = Signal()

    def __init__(self, store: TaskStore, today: date | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("weeklyFocusPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.store = store
        self.today = today or date.today()
        self.service = DashboardService(store.repository.db_path)
        layout = QVBoxLayout(self)
        heading=QLabel("Wochenfokus"); heading.setObjectName("laneTitle"); layout.addWidget(heading)
        self.goals_label = QLabel()
        self.goal_checks = []
        for index in range(3):
            check = QCheckBox(); check.setObjectName(f"weekly_goal_{index+1}")
            check.clicked.connect(lambda done, position=index+1: self._set_goal_done(position, done))
            self.goal_checks.append(check); layout.addWidget(check)
        self.deadline_label = QLabel()
        self.delegation_label = QLabel()
        self.follow_up_label = QLabel()
        self.progress_label = QLabel()
        for widget in (self.goals_label, self.deadline_label, self.delegation_label, self.follow_up_label, self.progress_label):
            widget.setWordWrap(True)
            layout.addWidget(widget)
        layout.addStretch(1)
        self.review_button = PrimaryButton("Wochenreview starten")
        self.review_button.setObjectName("weekly_review_start")
        self.review_button.clicked.connect(self.review_requested)
        layout.addWidget(self.review_button)
        store.changed.connect(self._on_change)
        self.refresh()

    def refresh(self) -> None:
        snapshot = self.service.weekly_focus(self.today)
        for index, check in enumerate(self.goal_checks):
            check.setVisible(index < len(snapshot.goals))
            if index < len(snapshot.goals):
                check.setText(snapshot.goals[index].title); check.setToolTip(snapshot.goals[index].title)
                check.setChecked(snapshot.goals[index].done)
        self.goals_label.setVisible(not snapshot.goals)
        self.goals_label.setText("\n".join(("✓ " if goal.done else "○ ") + goal.title for goal in snapshot.goals) or "Noch keine Wochenziele")
        self.deadline_label.setText("Nächste Deadline: " + (snapshot.next_deadline or "–"))
        self.delegation_label.setText("Älteste Delegation: " + (snapshot.oldest_delegation or "–"))
        self.follow_up_label.setText("Nächste Wiedervorlage: " + (snapshot.next_follow_up or "–"))
        self.progress_label.setText(f"Wochenfortschritt: {snapshot.progress_percent} %")

    def _on_change(self, change: ChangeSet) -> None:
        if "dashboard" in change.domains:
            self.refresh()

    def _set_goal_done(self, position, done):
        year, week, _ = self.today.isocalendar()
        connection = sqlite3.connect(self.store.repository.db_path)
        connection.execute("UPDATE weekly_goals SET done=? WHERE year=? AND week=? AND position=?", (int(done), year, week, position))
        connection.commit(); connection.close()
        self.store.changed.emit(ChangeSet(frozenset(), frozenset({"dashboard"})))
