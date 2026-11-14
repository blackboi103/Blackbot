from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.task_models import Task, TaskCreate, TaskEvent, TaskUpdate


SCHEMA_VERSION = 1


class TaskNotFoundError(LookupError):
    pass


class TaskStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            current_version = connection.execute("PRAGMA user_version").fetchone()[0]
            if current_version not in (0, SCHEMA_VERSION):
                raise RuntimeError(
                    f"Unsupported task database schema version: {current_version}"
                )
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL CHECK (
                        status IN ('backlog', 'ready', 'in_progress', 'review', 'done')
                    ),
                    priority TEXT NOT NULL CHECK (
                        priority IN ('low', 'medium', 'high')
                    ),
                    owner TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    position INTEGER NOT NULL DEFAULT 0 CHECK (position >= 0),
                    archived INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1)),
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS task_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    from_status TEXT,
                    to_status TEXT,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );

                CREATE INDEX IF NOT EXISTS idx_tasks_status
                ON tasks(archived, status, position, updated_at DESC);

                CREATE INDEX IF NOT EXISTS idx_task_events_created
                ON task_events(created_at DESC, id DESC);
                """
            )
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def list_tasks(self, include_archived: bool = False) -> list[Task]:
        query = "SELECT * FROM tasks"
        parameters: tuple[int, ...] = ()
        if not include_archived:
            query += " WHERE archived = ?"
            parameters = (0,)
        query += """
            ORDER BY
                CASE status
                    WHEN 'backlog' THEN 1
                    WHEN 'ready' THEN 2
                    WHEN 'in_progress' THEN 3
                    WHEN 'review' THEN 4
                    WHEN 'done' THEN 5
                END,
                position ASC,
                updated_at DESC,
                id ASC
        """
        with self._connection() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._task_from_row(row) for row in rows]

    def get_task(self, task_id: str) -> Task:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        if row is None:
            raise TaskNotFoundError(task_id)
        return self._task_from_row(row)

    def create_task(self, task_data: TaskCreate) -> Task:
        task_id = str(uuid4())
        timestamp = self._timestamp()
        with self._connection() as connection:
            position = self._next_position(connection, task_data.status.value)
            connection.execute(
                """
                INSERT INTO tasks (
                    id, title, description, status, priority, owner, tag, position,
                    archived, version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 1, ?, ?)
                """,
                (
                    task_id,
                    task_data.title,
                    task_data.description,
                    task_data.status.value,
                    task_data.priority.value,
                    task_data.owner,
                    task_data.tag,
                    position,
                    timestamp,
                    timestamp,
                ),
            )
            self._record_event(
                connection,
                task_id=task_id,
                event_type="created",
                from_status=None,
                to_status=task_data.status.value,
                detail=f"Task created in {task_data.status.value}.",
                timestamp=timestamp,
            )
        return self.get_task(task_id)

    def update_task(self, task_id: str, task_update: TaskUpdate) -> Task:
        current = self.get_task(task_id)
        changes = task_update.model_dump(exclude_unset=True)
        normalized_changes = {
            key: value.value if hasattr(value, "value") else value
            for key, value in changes.items()
        }
        next_status = normalized_changes.get("status")
        assignments = [f"{field} = ?" for field in normalized_changes]
        timestamp = self._timestamp()
        values = list(normalized_changes.values())
        assignments.extend(["version = version + 1", "updated_at = ?"])
        values.extend([timestamp, task_id])

        with self._connection() as connection:
            if next_status is not None and next_status != current.status.value:
                assignments.append("position = ?")
                values.insert(-1, self._next_position(connection, next_status))
            cursor = connection.execute(
                f"UPDATE tasks SET {', '.join(assignments)} WHERE id = ?",
                values,
            )
            if cursor.rowcount != 1:
                raise TaskNotFoundError(task_id)

            if next_status is not None and next_status != current.status.value:
                self._record_event(
                    connection,
                    task_id=task_id,
                    event_type="status_changed",
                    from_status=current.status.value,
                    to_status=next_status,
                    detail=f"Task moved from {current.status.value} to {next_status}.",
                    timestamp=timestamp,
                )
            else:
                self._record_event(
                    connection,
                    task_id=task_id,
                    event_type="updated",
                    from_status=current.status.value,
                    to_status=current.status.value,
                    detail="Task details updated.",
                    timestamp=timestamp,
                )
        return self.get_task(task_id)

    def archive_task(self, task_id: str) -> None:
        current = self.get_task(task_id)
        if current.archived:
            return
        timestamp = self._timestamp()
        with self._connection() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET archived = 1, version = version + 1, updated_at = ?
                WHERE id = ?
                """,
                (timestamp, task_id),
            )
            self._record_event(
                connection,
                task_id=task_id,
                event_type="archived",
                from_status=current.status.value,
                to_status=current.status.value,
                detail="Task archived.",
                timestamp=timestamp,
            )

    def list_events(self, limit: int = 50) -> list[TaskEvent]:
        bounded_limit = max(1, min(limit, 200))
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT task_events.*, tasks.title AS task_title
                FROM task_events
                JOIN tasks ON tasks.id = task_events.task_id
                ORDER BY task_events.created_at DESC, task_events.id DESC
                LIMIT ?
                """,
                (bounded_limit,),
            ).fetchall()
        return [TaskEvent.model_validate(dict(row)) for row in rows]

    @staticmethod
    def _record_event(
        connection: sqlite3.Connection,
        *,
        task_id: str,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        detail: str,
        timestamp: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO task_events (
                task_id, event_type, from_status, to_status, detail, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (task_id, event_type, from_status, to_status, detail, timestamp),
        )

    @staticmethod
    def _next_position(connection: sqlite3.Connection, status: str) -> int:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(position), -1) + 1
            FROM tasks
            WHERE status = ? AND archived = 0
            """,
            (status,),
        ).fetchone()
        return int(row[0])

    @staticmethod
    def _task_from_row(row: sqlite3.Row) -> Task:
        data = dict(row)
        data["archived"] = bool(data["archived"])
        return Task.model_validate(data)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
