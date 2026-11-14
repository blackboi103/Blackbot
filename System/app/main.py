from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.task_models import Task, TaskCreate, TaskEvent, TaskUpdate
from app.task_store import TaskNotFoundError, TaskStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
DATA_DIR = PROJECT_ROOT / "data"
TASK_DATABASE_PATH = DATA_DIR / "mission_control.db"

task_store = TaskStore(TASK_DATABASE_PATH)


@asynccontextmanager
async def lifespan(application: FastAPI):
    task_store.initialize()
    application.state.task_store = task_store
    yield


app = FastAPI(title="OpenClaw Mission Control", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_task_store(request: Request) -> TaskStore:
    return request.app.state.task_store


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks", response_model=list[Task])
def list_tasks(
    include_archived: bool = False,
    store: TaskStore = Depends(get_task_store),
) -> list[Task]:
    return store.list_tasks(include_archived=include_archived)


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: str,
    store: TaskStore = Depends(get_task_store),
) -> Task:
    try:
        return store.get_task(task_id)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error


@app.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    store: TaskStore = Depends(get_task_store),
) -> Task:
    return store.create_task(task_data)


@app.patch("/api/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    store: TaskStore = Depends(get_task_store),
) -> Task:
    try:
        return store.update_task(task_id, task_update)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_task(
    task_id: str,
    store: TaskStore = Depends(get_task_store),
) -> Response:
    try:
        store.archive_task(task_id)
    except TaskNotFoundError as error:
        raise HTTPException(status_code=404, detail="Task not found") from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/activity", response_model=list[TaskEvent])
def list_activity(
    limit: int = Query(default=50, ge=1, le=200),
    store: TaskStore = Depends(get_task_store),
) -> list[TaskEvent]:
    return store.list_events(limit=limit)
