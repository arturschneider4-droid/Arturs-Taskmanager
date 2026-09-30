from datetime import datetime
import sqlite3
from time import perf_counter

from taskmanager.navigation import Route
from taskmanager.repositories import QuerySpec, TaskRepository
from taskmanager.task_store import TaskStore
from taskmanager.v10_shell import V10Shell


def _seed(path, count=1000):
    connection = sqlite3.connect(path); now = datetime.now().isoformat()
    connection.executemany("INSERT INTO tasks(title,description,priority,status,recurrence,created_at,updated_at) VALUES(?,?,?,?,?,?,?)", [(f"Aufgabe {i}", "", "important_not_urgent", "Offen", "none", now, now) for i in range(count)])
    connection.commit(); connection.close()


def test_search_under_200ms_with_1000_tasks(v10_database):
    _seed(v10_database); repository = TaskRepository(v10_database)
    start = perf_counter(); result = repository.query(QuerySpec(search="Aufgabe 99")); elapsed = perf_counter() - start
    assert result and elapsed < .2


def test_start_under_two_seconds_and_cached_route_switch_under_150ms(qtbot, v10_database):
    _seed(v10_database); start = perf_counter(); shell = V10Shell(TaskStore(TaskRepository(v10_database))); elapsed = perf_counter() - start
    qtbot.addWidget(shell); assert elapsed < 2
    start = perf_counter(); shell.navigate(Route.TASKS); first_switch = perf_counter() - start
    assert first_switch < .15
    shell.page_for(Route.MY_DAY)
    start = perf_counter()
    for _ in range(10): shell.navigate(Route.MY_DAY); shell.navigate(Route.TASKS)
    assert (perf_counter() - start) / 20 < .15
