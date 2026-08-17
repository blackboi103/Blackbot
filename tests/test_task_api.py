import pytest
from fastapi import HTTPException

from app.main import archive_task, create_task, get_task, list_activity, list_tasks, update_task
from app.task_models import TaskCreate, TaskStatus, TaskUpdate
from app.task_store import TaskStore


@pytest.fixture
def task_store(tmp_path):
    store = TaskStore(tmp_path / "mission-control.db")
    store.initialize()
    return store


def test_task_api_functions_cover_create_list_update_and_archive(task_store):
    created = create_task(
        TaskCreate(title="API task", owner="Kyle", tag="Backend"),
        store=task_store,
    )
    listed = list_tasks(store=task_store)
    updated = update_task(
        created.id,
        TaskUpdate(status=TaskStatus.REVIEW),
        store=task_store,
    )
    events = list_activity(limit=50, store=task_store)
    response = archive_task(created.id, store=task_store)

    assert listed[0].id == created.id
    assert updated.status == TaskStatus.REVIEW
    assert events[0].event_type == "status_changed"
    assert response.status_code == 204
    assert list_tasks(store=task_store) == []


def test_task_api_translates_missing_task_to_404(task_store):
    with pytest.raises(HTTPException) as error:
        get_task("missing", store=task_store)

    assert error.value.status_code == 404
    assert error.value.detail == "Task not found"
