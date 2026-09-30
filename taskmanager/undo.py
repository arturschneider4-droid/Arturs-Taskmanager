from __future__ import annotations

import sqlite3


class UndoManager:
    def __init__(self, repository): self.repository = repository; self._stack = []
    @property
    def can_undo(self): return bool(self._stack)
    def capture(self, task_id):
        record = self.repository.get(task_id)
        if record is not None: self._stack.append(record)
    def undo(self):
        if not self._stack: return False
        record = self._stack.pop()
        if self.repository.get(record.id) is None:
            connection = sqlite3.connect(self.repository.db_path)
            connection.execute(
                "INSERT INTO tasks(id,title,description,priority,status,recurrence,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                (record.id, record.draft.title, record.draft.description, record.draft.priority, record.draft.status, record.draft.recurrence, record.created_at.isoformat(), record.updated_at.isoformat()),
            )
            connection.commit(); connection.close()
        self.repository.save(record.draft, record.id)
        return True
