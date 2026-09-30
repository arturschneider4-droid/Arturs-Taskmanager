PRAGMA foreign_keys=ON;
CREATE TABLE projects(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL UNIQUE);
CREATE TABLE tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',project_id INTEGER,priority TEXT NOT NULL DEFAULT 'important_not_urgent',due_date TEXT,status TEXT NOT NULL DEFAULT 'Offen',recurrence TEXT NOT NULL DEFAULT 'none',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL);
CREATE TABLE subtasks(id INTEGER PRIMARY KEY AUTOINCREMENT,task_id INTEGER NOT NULL,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0,FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE);
INSERT INTO projects(id,name) VALUES(1,'Vertrieb');
INSERT INTO tasks(id,title,description,project_id,priority,due_date,status,recurrence,created_at,updated_at) VALUES
 (1,'Angebot prüfen','Konditionen prüfen',1,'important_urgent','2026-10-02','Offen','weekly','2026-09-20 08:00:00','2026-09-25 09:00:00'),
 (2,'Archiviert','Abgeschlossen',NULL,'not_important_not_urgent',NULL,'Erledigt','none','2026-09-01 08:00:00','2026-09-02 09:00:00');
INSERT INTO subtasks(id,task_id,title,done) VALUES(1,1,'Preisliste öffnen',1);
