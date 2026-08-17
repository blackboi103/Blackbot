import sqlite3

import pytest
from pydantic import ValidationError

from app.task_models import TaskCreate, TaskStatus, TaskUpdate
from app.task_store import TaskStore


@pytest.fixture
def task_store(tmp_path):
    store = TaskStore(tmp_path / "mission-control.db")
    store.initialize()
    return store


def test_initialize_creates_versioned_schema(task_store):
    with sqlite3.connect(task_store.database_path) as connection:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert version == 1
    assert {"tasks", "task_events"}.issubset(table_names)


def test_create_and_move_task_records_activity(task_store):
    created = task_store.create_task(
        TaskCreate(
            title="Design task schema",
            description="Create the first Mission Control persistence model.",
            priority="high",
            owner="Kyle",
            tag="Architecture",
        )
    )

    updated = task_store.update_task(
        created.id,
        TaskUpdate(status=TaskStatus.IN_PROGRESS),
    )
    events = task_store.list_events()

    assert created.status == TaskStatus.BACKLOG
    assert created.position == 0
    assert updated.status == TaskStatus.IN_PROGRESS
    assert updated.position == 0
    assert updated.version == 2
    assert [event.event_type for event in events] == ["status_changed", "created"]
    assert events[0].from_status == TaskStatus.BACKLOG
    assert events[0].to_status == TaskStatus.IN_PROGRESS
    assert events[0].task_title == "Design task schema"


def test_tasks_receive_stable_positions_within_a_column(task_store):
    first = task_store.create_task(TaskCreate(title="First task"))
    second = task_store.create_task(TaskCreate(title="Second task"))

    listed = task_store.list_tasks()

    assert first.position == 0
    assert second.position == 1
    assert [task.title for task in listed] == ["First task", "Second task"]


def test_archive_hides_task_without_destroying_history(task_store):
    task = task_store.create_task(TaskCreate(title="Temporary task"))

    task_store.archive_task(task.id)

    assert task_store.list_tasks() == []
    assert task_store.list_tasks(include_archived=True)[0].archived is True
    assert task_store.get_task(task.id).archived is True
    assert task_store.list_events()[0].event_type == "archived"


def test_task_update_rejects_empty_or_null_patch():
    with pytest.raises(ValidationError):
        TaskUpdate()

    with pytest.raises(ValidationError):
        TaskUpdate(title=None)
