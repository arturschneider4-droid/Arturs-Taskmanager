from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
import sqlite3
import calendar

from .task_model import ControlMode, TaskDraft, TaskRecord


@dataclass(frozen=True)
class QuerySpec:
    search: str = ""
    project_id: int | None = None
    priority: str | None = None
    status: str | None = None
    control_mode: ControlMode | None = None
    planned_from: date | None = None
    planned_to: date | None = None
    limit: int = 1000
    metric_filter: str | None = None
    today: date | None = None
    without_project: bool = False
    deadline_filter: str = ""
    archived: bool | None = False


@dataclass(frozen=True)
class TaskSummary:
    id: int
    title: str
    project_name: str | None
    priority: str
    status: str
    planning_date: date | None
    deadline: date | None
    control_mode: ControlMode
    responsible_party: str | None
    is_top_three: bool
    follow_up_date: date | None = None
    archived_at: datetime | None = None


@dataclass(frozen=True)
class DashboardMetrics:
    today_open: int
    overdue: int
    due_follow_ups: int
    delegated_open: int
    top_three: int
    critical_next_seven_days: int
    unplanned: int
    completed_this_week: int


def _iso(value):
    return value.isoformat() if value is not None else None


class TaskRepository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def save(self, draft: TaskDraft, task_id: int | None = None) -> int:
        self.last_created_recurrence_id = None
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute("SELECT status,completed_at,archived_at FROM tasks WHERE id=?", (task_id,)).fetchone() if task_id is not None else None
            if draft.is_top_three:
                sql = "SELECT COUNT(*) FROM tasks WHERE is_top_three=1 AND status!='Erledigt'"
                params = ()
                if task_id is not None:
                    sql += " AND id!=?"
                    params = (task_id,)
                if connection.execute(sql, params).fetchone()[0] >= 3:
                    raise ValueError("Top 3 enthält bereits drei aktive Aufgaben")
            now = datetime.now().isoformat(timespec="seconds")
            values = (
                draft.title, draft.description, draft.project_id, draft.priority,
                _iso(draft.deadline), draft.status, draft.recurrence,
                _iso(draft.planning_date), _iso(draft.planning_time), _iso(draft.deadline),
                draft.estimated_minutes, int(draft.is_top_three), int(draft.reminder_enabled),
                _iso(draft.reminder_at), draft.reminder_lead_minutes, draft.control_mode.value,
                draft.responsible_party, _iso(draft.delegated_at), _iso(draft.last_contact_at),
                _iso(draft.expected_response_at), _iso(draft.follow_up_date), now,
            )
            if task_id is None:
                task_id = connection.execute("""
                    INSERT INTO tasks(title,description,project_id,priority,due_date,status,recurrence,
                    planning_date,planning_time,deadline,estimated_minutes,is_top_three,reminder_enabled,
                    reminder_at,reminder_lead_minutes,control_mode,responsible_party,delegated_at,last_contact_at,
                    expected_response_at,follow_up_date,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, values[:-1] + (now, now)).lastrowid
            else:
                connection.execute("""
                    UPDATE tasks SET title=?,description=?,project_id=?,priority=?,due_date=?,status=?,recurrence=?,
                    planning_date=?,planning_time=?,deadline=?,estimated_minutes=?,is_top_three=?,reminder_enabled=?,
                    reminder_at=?,reminder_lead_minutes=?,control_mode=?,responsible_party=?,delegated_at=?,last_contact_at=?,
                    expected_response_at=?,follow_up_date=?,updated_at=? WHERE id=?
                """, values + (task_id,))
                connection.execute("DELETE FROM subtasks WHERE task_id=?", (task_id,))
                connection.execute("DELETE FROM task_people WHERE task_id=?", (task_id,))
            completed_at = archived_at = None
            if draft.status == "Erledigt":
                completed_at = (previous["completed_at"] or now) if previous and previous["status"] == "Erledigt" else now
                archived_at = previous["archived_at"] if previous and previous["status"] == "Erledigt" else None
            connection.execute("UPDATE tasks SET completed_at=?,archived_at=? WHERE id=?", (completed_at, archived_at, task_id))
            for title, done in draft.subtasks:
                if title.strip():
                    connection.execute("INSERT INTO subtasks(task_id,title,done) VALUES(?,?,?)", (task_id, title.strip(), int(done)))
            for person in dict.fromkeys(tag.strip() for tag in draft.people_tags if tag.strip()):
                connection.execute("INSERT INTO task_people(task_id,person) VALUES(?,?)", (task_id, person))
            if previous and previous["status"] != "Erledigt" and draft.status == "Erledigt" and draft.recurrence != "none":
                anchor = draft.planning_date or draft.deadline or date.today()
                if draft.recurrence == "monthly":
                    month = anchor.month % 12 + 1; year = anchor.year + (anchor.month == 12)
                    target = date(year, month, min(anchor.day, calendar.monthrange(year, month)[1]))
                else:
                    target = anchor + timedelta(days=7 if draft.recurrence == "weekly" else 1)
                offset = target - anchor
                row = dict(connection.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())
                row.pop("id")
                row.update(status="Offen", is_top_three=0, created_at=now, updated_at=now, completed_at=None, archived_at=None)
                row["planning_date"] = target.isoformat()
                for key in ("deadline", "due_date", "follow_up_date"):
                    if row.get(key): row[key] = (date.fromisoformat(row[key]) + offset).isoformat()
                if row.get("reminder_at"): row["reminder_at"] = (datetime.fromisoformat(row["reminder_at"]) + offset).isoformat()
                columns = ','.join(row)
                marks = ','.join('?' for _ in row)
                next_id = connection.execute(f"INSERT INTO tasks({columns}) VALUES({marks})", tuple(row.values())).lastrowid
                connection.execute("INSERT INTO subtasks(task_id,title,done) SELECT ?,title,0 FROM subtasks WHERE task_id=?", (next_id,task_id))
                connection.execute("INSERT INTO task_people(task_id,person) SELECT ?,person FROM task_people WHERE task_id=?", (next_id,task_id))
                self.last_created_recurrence_id = next_id
            connection.commit()
            return int(task_id)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def get(self, task_id: int) -> TaskRecord | None:
        connection = self._connect()
        row = connection.execute("SELECT t.*,p.name project_name FROM tasks t LEFT JOIN projects p ON p.id=t.project_id WHERE t.id=?", (task_id,)).fetchone()
        if row is None:
            connection.close()
            return None
        subtasks = tuple((item["title"], bool(item["done"])) for item in connection.execute("SELECT title,done FROM subtasks WHERE task_id=? ORDER BY id", (task_id,)))
        people = tuple(item[0] for item in connection.execute("SELECT person FROM task_people WHERE task_id=? ORDER BY person", (task_id,)))
        connection.close()
        draft = TaskDraft(
            title=row["title"], description=row["description"], project_id=row["project_id"],
            priority=row["priority"], status=row["status"], subtasks=subtasks, recurrence=row["recurrence"],
            planning_date=date.fromisoformat(row["planning_date"]) if row["planning_date"] else None,
            planning_time=time.fromisoformat(row["planning_time"]) if row["planning_time"] else None,
            deadline=date.fromisoformat(row["deadline"]) if row["deadline"] else None,
            estimated_minutes=row["estimated_minutes"], is_top_three=bool(row["is_top_three"]),
            reminder_enabled=bool(row["reminder_enabled"]),
            reminder_at=datetime.fromisoformat(row["reminder_at"]) if row["reminder_at"] else None,
            reminder_lead_minutes=row["reminder_lead_minutes"], control_mode=ControlMode(row["control_mode"]),
            responsible_party=row["responsible_party"], delegated_at=datetime.fromisoformat(row["delegated_at"]) if row["delegated_at"] else None,
            last_contact_at=datetime.fromisoformat(row["last_contact_at"]) if row["last_contact_at"] else None,
            expected_response_at=datetime.fromisoformat(row["expected_response_at"]) if row["expected_response_at"] else None,
            follow_up_date=date.fromisoformat(row["follow_up_date"]) if row["follow_up_date"] else None,
            people_tags=people,
        )
        return TaskRecord(task_id, draft, datetime.fromisoformat(row["created_at"]), datetime.fromisoformat(row["updated_at"]), row["project_name"],
                          datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                          datetime.fromisoformat(row["archived_at"]) if row["archived_at"] else None)

    def archive_completed(self, now: datetime | None = None) -> frozenset[int]:
        now = now or datetime.now()
        cutoff = (now - timedelta(days=7)).isoformat(timespec="seconds")
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                "UPDATE tasks SET archived_at=? WHERE status='Erledigt' AND archived_at IS NULL "
                "AND datetime(completed_at)<=datetime(?) RETURNING id",
                (now.isoformat(timespec="seconds"), cutoff),
            ).fetchall()
            connection.commit()
            return frozenset(row[0] for row in rows)
        finally:
            connection.close()

    def delete(self, task_id: int) -> None:
        connection = self._connect()
        connection.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        connection.commit()
        connection.close()

    def replace_top_three(self, promoted_task_id: int, replaced_task_id: int | None = None) -> None:
        """Promote one task while enforcing the active Top-3 invariant atomically."""
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            promoted = connection.execute("SELECT id,status FROM tasks WHERE id=?", (promoted_task_id,)).fetchone()
            if promoted is None or promoted["status"] == "Erledigt":
                raise ValueError("Nur aktive Aufgaben können zu Top 3 gehören")
            count = connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE is_top_three=1 AND status!='Erledigt' AND id!=?",
                (promoted_task_id,),
            ).fetchone()[0]
            if count >= 3:
                if replaced_task_id is None:
                    raise ValueError("Top 3 enthält bereits drei aktive Aufgaben")
                replaced = connection.execute(
                    "SELECT id FROM tasks WHERE id=? AND is_top_three=1 AND status!='Erledigt'",
                    (replaced_task_id,),
                ).fetchone()
                if replaced is None:
                    raise ValueError("Zu ersetzende Top-3-Aufgabe wurde nicht gefunden")
                connection.execute("UPDATE tasks SET is_top_three=0 WHERE id=?", (replaced_task_id,))
            connection.execute("UPDATE tasks SET is_top_three=1,updated_at=? WHERE id=?", (datetime.now().isoformat(timespec="seconds"), promoted_task_id))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def query(self, spec: QuerySpec | None = None) -> list[TaskSummary]:
        spec = spec or QuerySpec()
        connection = self._connect()
        sql = """SELECT t.id,t.title,p.name project_name,t.priority,t.status,t.planning_date,
                 t.deadline,t.control_mode,t.responsible_party,t.is_top_three,t.follow_up_date,t.archived_at
                 FROM tasks t LEFT JOIN projects p ON p.id=t.project_id WHERE 1=1"""
        params = []
        if spec.archived is not None:
            sql += " AND t.archived_at IS " + ("NOT NULL" if spec.archived else "NULL")
        if spec.metric_filter:
            today = spec.today or date.today()
            filters = {
                "today": ("status!='Erledigt' AND planning_date=?", (today.isoformat(),)),
                "overdue": ("status!='Erledigt' AND deadline<?", (today.isoformat(),)),
                "follow_ups": ("status!='Erledigt' AND follow_up_date<=?", (today.isoformat(),)),
                "delegated": ("status!='Erledigt' AND control_mode='delegated'", ()),
                "top_three": ("status!='Erledigt' AND is_top_three=1", ()),
                "critical_deadlines": ("status!='Erledigt' AND deadline BETWEEN ? AND ?", (today.isoformat(), (today + timedelta(days=7)).isoformat())),
                "unplanned": ("status!='Erledigt' AND planning_date IS NULL AND follow_up_date IS NULL", ()),
                "week_progress": ("status='Erledigt' AND date(updated_at) BETWEEN ? AND ?", ((today-timedelta(days=today.weekday())).isoformat(), (today+timedelta(days=6-today.weekday())).isoformat())),
            }
            clause, values = filters[spec.metric_filter]
            sql += " AND (" + clause + ")"; params.extend(values)
        if spec.deadline_filter:
            today = spec.today or date.today()
            deadline_clauses = {
                "overdue": ("t.deadline<? AND t.status!='Erledigt'", (today.isoformat(),)),
                "today": ("t.deadline=?", (today.isoformat(),)),
                "next7": ("t.deadline BETWEEN ? AND ?", (today.isoformat(), (today + timedelta(days=6)).isoformat())),
                "none": ("t.deadline IS NULL", ()),
            }
            clause, values = deadline_clauses[spec.deadline_filter]
            sql += " AND (" + clause + ")"; params.extend(values)
        if spec.search:
            sql += " AND (LOWER(t.title) LIKE ? OR LOWER(t.description) LIKE ?)"
            value = f"%{spec.search.lower()}%"
            params.extend((value, value))
        if spec.without_project:
            sql += " AND t.project_id IS NULL"
        if spec.project_id is not None:
            sql += " AND t.project_id=?"
            params.append(spec.project_id)
        if spec.priority is not None:
            sql += " AND t.priority=?"
            params.append(spec.priority)
        if spec.status is not None:
            sql += " AND t.status=?"
            params.append(spec.status)
        if spec.control_mode is not None:
            sql += " AND t.control_mode=?"
            params.append(ControlMode(spec.control_mode).value)
        if spec.planned_from is not None:
            sql += " AND t.planning_date>=?"
            params.append(spec.planned_from.isoformat())
        if spec.planned_to is not None:
            sql += " AND t.planning_date<=?"
            params.append(spec.planned_to.isoformat())
        sql += " ORDER BY CASE WHEN t.planning_date IS NULL THEN 1 ELSE 0 END,t.planning_date,t.id DESC LIMIT ?"
        params.append(max(1, min(spec.limit, 5000)))
        rows = connection.execute(sql, params).fetchall()
        connection.close()
        return [TaskSummary(
            id=row["id"], title=row["title"], project_name=row["project_name"],
            priority=row["priority"], status=row["status"],
            planning_date=date.fromisoformat(row["planning_date"]) if row["planning_date"] else None,
            deadline=date.fromisoformat(row["deadline"]) if row["deadline"] else None,
            control_mode=ControlMode(row["control_mode"]), responsible_party=row["responsible_party"],
            is_top_three=bool(row["is_top_three"]),
            follow_up_date=date.fromisoformat(row["follow_up_date"]) if row["follow_up_date"] else None,
            archived_at=datetime.fromisoformat(row["archived_at"]) if row["archived_at"] else None,
        ) for row in rows]


class DashboardRepository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def metrics(self, today: date) -> DashboardMetrics:
        week_start = today - timedelta(days=today.weekday())
        week_end = today + timedelta(days=6 - today.weekday())
        connection = sqlite3.connect(self.db_path)
        row = connection.execute("""
            SELECT
              COALESCE(SUM(status!='Erledigt' AND planning_date=?),0),
              COALESCE(SUM(status!='Erledigt' AND deadline<?),0),
              COALESCE(SUM(status!='Erledigt' AND follow_up_date<=?),0),
              COALESCE(SUM(status!='Erledigt' AND control_mode='delegated'),0),
              COALESCE(SUM(status!='Erledigt' AND is_top_three=1),0),
              COALESCE(SUM(status!='Erledigt' AND deadline BETWEEN ? AND ?),0),
              COALESCE(SUM(status!='Erledigt' AND planning_date IS NULL AND follow_up_date IS NULL),0),
              COALESCE(SUM(status='Erledigt' AND date(updated_at) BETWEEN ? AND ?),0)
            FROM tasks
        """, (today.isoformat(), today.isoformat(), today.isoformat(), today.isoformat(),
              (today + timedelta(days=7)).isoformat(), week_start.isoformat(), week_end.isoformat())).fetchone()
        connection.close()
        return DashboardMetrics(*(int(value) for value in row))
