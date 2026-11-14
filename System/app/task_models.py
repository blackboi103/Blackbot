from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskStatus(StrEnum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=400)
    status: TaskStatus = TaskStatus.BACKLOG
    priority: TaskPriority = TaskPriority.MEDIUM
    owner: str = Field(default="Unassigned", max_length=80)
    tag: str = Field(default="General", max_length=40)

    @field_validator("title", "owner", "tag")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        return value.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=400)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    owner: str | None = Field(default=None, max_length=80)
    tag: str | None = Field(default=None, max_length=40)

    @field_validator("title", "owner", "tag")
    @classmethod
    def strip_optional_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_optional_description(cls, value: str | None) -> str | None:
        return None if value is None else value.strip()

    @model_validator(mode="after")
    def require_change(self) -> TaskUpdate:
        if not self.model_fields_set:
            raise ValueError("at least one task field must be provided")
        if any(getattr(self, field_name) is None for field_name in self.model_fields_set):
            raise ValueError("task fields cannot be null")
        return self


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    owner: str
    tag: str
    position: int
    archived: bool
    version: int
    created_at: datetime
    updated_at: datetime


class TaskEvent(BaseModel):
    id: int
    task_id: str
    task_title: str
    event_type: str
    from_status: TaskStatus | None
    to_status: TaskStatus | None
    detail: str
    created_at: datetime
