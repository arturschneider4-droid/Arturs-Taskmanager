from datetime import date
import sqlite3
from time import perf_counter

import pytest

from taskmanager.repositories import DashboardRepository, QuerySpec, TaskRepository
from tests.v10.test_migrations import make_legacy_database
from taskmanager.migrations import migrate_to_v10


@pytest.mark.parametrize("count,max_seconds", [(100, 0.08), (1000, 0.15), (5000, 0.20)])
def test_search_and_dashboard_queries_stay_within_budget(tmp_path, count, max_seconds):
    path = tmp_path / "tasks.db"
    make_legacy_database(path)
    migrate_to_v10(path, tmp_path / "backups")
    connection = sqlite3.connect(path)
    rows = [
        (f"Aufgabe {index} Labor" if index % 50 == 0 else f"Aufgabe {index}", "", "important_not_urgent", "Offen", "none", "2026-09-26", "2026-09-26")
        for index in range(count)
    ]
    connection.executemany("INSERT INTO tasks(title,description,priority,status,recurrence,created_at,updated_at) VALUES(?,?,?,?,?,?,?)", rows)
    connection.commit()
    connection.close()

    started = perf_counter()
    result = TaskRepository(path).query(QuerySpec(search="labor", limit=200))
    metrics = DashboardRepository(path).metrics(date(2026, 9, 26))
    elapsed = perf_counter() - started

    assert len(result) == (count + 49) // 50
    assert metrics.unplanned >= count
    assert elapsed < max_seconds
