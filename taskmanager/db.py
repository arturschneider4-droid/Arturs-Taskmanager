from pathlib import Path
import sqlite3
import shutil
from datetime import datetime, date, timedelta

APP_DIR = Path.home() / "TaskManager"
DB_PATH = APP_DIR / "tasks.db"
BACKUP_DIR = APP_DIR / "backups"


def connect():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL UNIQUE);
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',
      project_id INTEGER,priority TEXT NOT NULL DEFAULT 'important_not_urgent',due_date TEXT,
      status TEXT NOT NULL DEFAULT 'Offen',recurrence TEXT NOT NULL DEFAULT 'none',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL);
    CREATE TABLE IF NOT EXISTS subtasks(id INTEGER PRIMARY KEY AUTOINCREMENT,task_id INTEGER NOT NULL,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0,
      FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE);
    CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
    CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    """)
    cols = {x["name"] for x in c.execute("PRAGMA table_info(tasks)")}
    if "recurrence" not in cols:
        c.execute("ALTER TABLE tasks ADD COLUMN recurrence TEXT NOT NULL DEFAULT 'none'")
    if "updated_at" not in cols:
        c.execute("ALTER TABLE tasks ADD COLUMN updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")
    c.commit(); c.close()


def backup_db(label="manual"):
    """Create a timestamped SQLite backup before destructive/edit operations."""
    if not DB_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target = BACKUP_DIR / f"{stamp}_{label}.db"
    shutil.copy2(DB_PATH, target)
    # Keep the most recent 20 backups.
    files = sorted(BACKUP_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in files[20:]:
        try: old.unlink()
        except OSError: pass
    return target


def restore_backup(path):
    """Restore a backup atomically enough for a local single-user application."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    if DB_PATH.exists():
        backup_db("before_restore")
    shutil.copy2(source, DB_PATH)


def latest_backup():
    files = sorted(BACKUP_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def task(tid):
    c=connect(); r=c.execute("SELECT t.*,p.name project_name FROM tasks t LEFT JOIN projects p ON p.id=t.project_id WHERE t.id=?",(tid,)).fetchone(); c.close(); return r


def subs(tid):
    c=connect(); r=c.execute("SELECT * FROM subtasks WHERE task_id=? ORDER BY id",(tid,)).fetchall(); c.close(); return r


def save(d, tid=None, make_backup=True):
    c=connect(); now=datetime.now().isoformat(timespec="seconds")
    if tid is not None and make_backup:
        c.close(); backup_db("before_save"); c=connect()
    if tid is None:
        cur=c.execute("INSERT INTO tasks(title,description,project_id,priority,due_date,status,recurrence,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
          (d["title"],d["description"],d["project_id"],d["priority"],d["due_date"],d["status"],d["recurrence"],now,now)); tid=cur.lastrowid
    else:
        c.execute("UPDATE tasks SET title=?,description=?,project_id=?,priority=?,due_date=?,status=?,recurrence=?,updated_at=? WHERE id=?",
          (d["title"],d["description"],d["project_id"],d["priority"],d["due_date"],d["status"],d["recurrence"],now,tid))
        c.execute("DELETE FROM subtasks WHERE task_id=?",(tid,))
    for title,done in d.get("subtasks",[]):
        if title and title.strip(): c.execute("INSERT INTO subtasks(task_id,title,done) VALUES(?,?,?)",(tid,title.strip(),int(done)))
    c.commit(); c.close(); return tid


def remove(tid):
    backup_db("before_delete")
    c=connect(); r=c.execute("SELECT * FROM tasks WHERE id=?",(tid,)).fetchone(); c.execute("DELETE FROM tasks WHERE id=?",(tid,)); c.commit(); c.close(); return r


def update_status(tid, status):
    backup_db("before_status")
    c=connect(); c.execute("UPDATE tasks SET status=?,updated_at=? WHERE id=?",(status,datetime.now().isoformat(timespec="seconds"),tid)); c.commit(); c.close()


def update_priority(tid, priority):
    backup_db("before_priority")
    c=connect(); c.execute("UPDATE tasks SET priority=?,updated_at=? WHERE id=?",(priority,datetime.now().isoformat(timespec="seconds"),tid)); c.commit(); c.close()


def update_due(tid, due_date):
    backup_db("before_due")
    c=connect(); c.execute("UPDATE tasks SET due_date=?,updated_at=? WHERE id=?",(due_date,datetime.now().isoformat(timespec="seconds"),tid)); c.commit(); c.close()


def tasks(project=None,search="",priority=None,status="Alle Status",due="Alle Fälligkeiten"):
    c=connect(); sql="SELECT t.*,p.name project_name FROM tasks t LEFT JOIN projects p ON p.id=t.project_id WHERE 1=1"; a=[]
    if project is not None: sql+=" AND t.project_id=?"; a.append(project)
    if search: sql+=" AND (LOWER(t.title) LIKE ? OR LOWER(t.description) LIKE ? OR EXISTS (SELECT 1 FROM subtasks s WHERE s.task_id=t.id AND LOWER(s.title) LIKE ?))"; q="%"+search.lower()+"%"; a += [q,q,q]
    if priority: sql+=" AND t.priority=?"; a.append(priority)
    if status!="Alle Status": sql+=" AND t.status=?"; a.append(status)
    today=date.today(); end=today+timedelta(days=6-today.weekday())
    if due=="Heute": sql+=" AND t.due_date=?"; a.append(today.isoformat())
    elif due=="Diese Woche": sql+=" AND t.due_date BETWEEN ? AND ?"; a += [today.isoformat(),end.isoformat()]
    elif due=="Später": sql+=" AND (t.due_date>? OR t.due_date IS NULL)"; a.append(end.isoformat())
    elif due=="Ohne Fälligkeit": sql+=" AND t.due_date IS NULL"
    sql+=" ORDER BY CASE priority WHEN 'important_urgent' THEN 1 WHEN 'important_not_urgent' THEN 2 WHEN 'not_important_urgent' THEN 3 ELSE 4 END, CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,due_date,id DESC"
    r=c.execute(sql,a).fetchall(); c.close(); return r
