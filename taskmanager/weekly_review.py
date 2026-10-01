from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import json
import sqlite3

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


REVIEW_STEPS = (
    "Eingang leeren", "Überfälliges entscheiden", "Warten und Delegiert prüfen",
    "Nächste sieben Tage", "Projekte prüfen", "Erfolge reflektieren", "Wochenfokus festlegen",
)


@dataclass(frozen=True)
class ReviewSession:
    id: int
    current_step: int
    answers: dict
    completed_at: datetime | None


@dataclass(frozen=True)
class ReviewSummary:
    steps_completed: int
    goals: tuple[str, ...]


class WeeklyReviewService:
    def __init__(self, db_path, today: date | None = None):
        self.db_path = db_path
        self.today = today or date.today()
        iso = self.today.isocalendar()
        self.year, self.week = iso.year, iso.week

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def start(self) -> ReviewSession:
        existing = self.resume()
        if existing:
            return existing
        connection = self._connect()
        now = datetime.now().isoformat(timespec="seconds")
        connection.execute(
            "INSERT INTO review_sessions(year,week,current_step,summary_json,updated_at) VALUES(?,?,?,?,?)",
            (self.year, self.week, 1, "{}", now),
        )
        connection.commit(); connection.close()
        return self.resume()

    def resume(self) -> ReviewSession | None:
        connection = self._connect()
        row = connection.execute(
            "SELECT * FROM review_sessions WHERE year=? AND week=? ORDER BY id DESC LIMIT 1",
            (self.year, self.week),
        ).fetchone()
        connection.close()
        if row is None:
            return None
        return ReviewSession(row["id"], row["current_step"], json.loads(row["summary_json"] or "{}"), datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None)

    def advance(self, answers: dict) -> ReviewSession:
        session = self.start()
        merged = dict(session.answers); merged.update(answers)
        step = min(7, session.current_step + 1)
        self._update(session.id, step, merged)
        return self.resume()

    def back(self) -> ReviewSession:
        session = self.start()
        self._update(session.id, max(1, session.current_step - 1), session.answers)
        return self.resume()

    def _update(self, session_id: int, step: int, answers: dict):
        connection = self._connect()
        connection.execute(
            "UPDATE review_sessions SET current_step=?,summary_json=?,updated_at=? WHERE id=?",
            (step, json.dumps(answers, ensure_ascii=False), datetime.now().isoformat(timespec="seconds"), session_id),
        )
        connection.commit(); connection.close()

    def set_goals(self, goals: list[str]):
        goals = [goal.strip() for goal in goals if goal.strip()]
        if len(goals) > 3:
            raise ValueError("Es sind maximal drei Wochenziele erlaubt")
        connection = self._connect()
        connection.execute("DELETE FROM weekly_goals WHERE year=? AND week=?", (self.year, self.week))
        for position, title in enumerate(goals, 1):
            connection.execute("INSERT INTO weekly_goals(year,week,title,position) VALUES(?,?,?,?)", (self.year, self.week, title, position))
        connection.commit(); connection.close()

    def goals(self) -> list[str]:
        connection = self._connect()
        rows = connection.execute("SELECT title FROM weekly_goals WHERE year=? AND week=? ORDER BY position", (self.year, self.week)).fetchall()
        connection.close()
        return [row[0] for row in rows]

    def complete(self) -> ReviewSummary:
        session = self.start()
        now = datetime.now().isoformat(timespec="seconds")
        connection = self._connect()
        connection.execute("UPDATE review_sessions SET current_step=7,completed_at=?,updated_at=? WHERE id=?", (now, now, session.id))
        connection.commit(); connection.close()
        return ReviewSummary(7, tuple(self.goals()))


class WeeklyReviewView(QWidget):
    completed = Signal(object)
    paused = Signal()

    def __init__(self, service: WeeklyReviewService, parent=None):
        super().__init__(parent)
        self.service = service
        self.session = service.start()
        root = QVBoxLayout(self)
        self.step_label = QLabel()
        self.answer_edit = QLineEdit()
        self.answer_edit.setPlaceholderText("Entscheidung oder Ergebnis festhalten")
        self.feedback_label = QLabel()
        self.back_button = QPushButton("Zurück")
        self.next_button = QPushButton("Weiter")
        self.cancel_button = QPushButton("Später fortsetzen")
        self.back_button.setObjectName("review_back"); self.next_button.setObjectName("review_next"); self.cancel_button.setObjectName("review_cancel")
        for widget in (self.step_label, self.answer_edit, self.feedback_label, self.back_button, self.next_button, self.cancel_button):
            root.addWidget(widget)
        root.addStretch(1)
        self.feedback_label.setWordWrap(True)
        self.step_label.setWordWrap(True)
        self.back_button.clicked.connect(self._back)
        self.next_button.clicked.connect(self._next)
        self.cancel_button.clicked.connect(self._pause)
        self._render()

    @property
    def step_number(self):
        return self.session.current_step

    def _render(self):
        self.step_label.setText(f"Schritt {self.step_number} von 7 · {REVIEW_STEPS[self.step_number - 1]}")
        self.back_button.setEnabled(self.step_number > 1)
        self.next_button.setText("Review abschließen" if self.step_number == 7 else "Weiter")
        self.answer_edit.setText(self.session.answers.get(f"step_{self.step_number}", ""))
        self.answer_edit.setPlaceholderText("Bis zu drei Wochenziele, getrennt durch ;" if self.step_number == 7 else "Entscheidung oder Ergebnis festhalten")
        self.feedback_label.clear()

    def _persist_answer(self):
        answers = dict(self.session.answers)
        answers[f"step_{self.step_number}"] = self.answer_edit.text()
        self.service._update(self.session.id, self.step_number, answers)
        self.session = self.service.resume()

    def _pause(self):
        self._persist_answer(); self.paused.emit(); self.hide()

    def _back(self):
        self._persist_answer()
        self.session = self.service.back(); self._render()

    def _next(self):
        answer = self.answer_edit.text().strip()
        if not answer:
            self.feedback_label.setText("Bitte eine Entscheidung festhalten")
            return
        if self.step_number == 7:
            goals = [part.strip() for part in answer.split(";") if part.strip()]
            try: self.service.set_goals(goals)
            except ValueError as error:
                self.feedback_label.setText(str(error)); return
            self._persist_answer()
            summary = self.service.complete()
            self.completed.emit(summary)
            return
        self.session = self.service.advance({f"step_{self.step_number}": answer})
        self._render()
