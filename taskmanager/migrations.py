from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import sqlite3


class MigrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class MigrationResult:
    from_version: int
    to_version: int
    backup_path: Path


TASK_COLUMNS = {
    "planning_date": "TEXT",
    "planning_time": "TEXT",
    "deadline": "TEXT",
    "estimated_minutes": "INTEGER",
    "is_top_three": "INTEGER NOT NULL DEFAULT 0 CHECK(is_top_three IN (0,1))",
    "reminder_enabled": "INTEGER NOT NULL DEFAULT 0 CHECK(reminder_enabled IN (0,1))",
    "reminder_at": "TEXT",
    "reminder_lead_minutes": "INTEGER",
    "control_mode": "TEXT NOT NULL DEFAULT 'self' CHECK(control_mode IN ('self','delegated','waiting'))",
    "responsible_party": "TEXT",
    "delegated_at": "TEXT",
    "last_contact_at": "TEXT",
    "expected_response_at": "TEXT",
    "follow_up_date": "TEXT",
}


def _validate_v10(connection: sqlite3.Connection) -> None:
    if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise MigrationError("Datenbankintegrität konnte nicht bestätigt werden")
    columns = {row[1] for row in connection.execute("PRAGMA table_info(tasks)")}
    if not set(TASK_COLUMNS) <= columns:
        raise MigrationError("V10-Aufgabenschema ist unvollständig")


def migrate_to_v10(db_path: Path, backup_dir: Path) -> MigrationResult:
    db_path = Path(db_path)
    backup_dir = Path(backup_dir)
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = backup_dir / f"{stamp}_before_v10.db"
    shutil.copy2(db_path, backup_path)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        columns = {row[1] for row in connection.execute("PRAGMA table_info(tasks)")}
        for name, declaration in TASK_COLUMNS.items():
            if name not in columns:
                connection.execute(f"ALTER TABLE tasks ADD COLUMN {name} {declaration}")
        connection.execute("UPDATE tasks SET deadline=due_date WHERE deadline IS NULL AND due_date IS NOT NULL")
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS schema_versions(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS weekly_goals(id INTEGER PRIMARY KEY AUTOINCREMENT,year INTEGER NOT NULL,week INTEGER NOT NULL,title TEXT NOT NULL,position INTEGER NOT NULL CHECK(position BETWEEN 1 AND 3),done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)),UNIQUE(year,week,position));
        CREATE TABLE IF NOT EXISTS review_sessions(id INTEGER PRIMARY KEY AUTOINCREMENT,year INTEGER NOT NULL,week INTEGER NOT NULL,current_step INTEGER NOT NULL DEFAULT 1,completed_at TEXT,summary_json TEXT NOT NULL DEFAULT '{}',updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS task_people(task_id INTEGER NOT NULL,person TEXT NOT NULL,PRIMARY KEY(task_id,person),FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS undo_log(id INTEGER PRIMARY KEY AUTOINCREMENT,command_type TEXT NOT NULL,payload_json TEXT NOT NULL,created_at TEXT NOT NULL,undone_at TEXT);
        CREATE INDEX IF NOT EXISTS idx_tasks_planning_date ON tasks(planning_date);
        CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);
        CREATE INDEX IF NOT EXISTS idx_tasks_follow_up_date ON tasks(follow_up_date);
        CREATE INDEX IF NOT EXISTS idx_tasks_control_mode ON tasks(control_mode);
        """)
        connection.execute(
            "INSERT OR REPLACE INTO schema_versions(version,applied_at) VALUES(10,?)",
            (datetime.now().isoformat(timespec="seconds"),),
        )
        _validate_v10(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        shutil.copy2(backup_path, db_path)
        raise
    finally:
        if connection:
            try:
                connection.close()
            except sqlite3.Error:
                pass
    return MigrationResult(from_version=9, to_version=10, backup_path=backup_path)

