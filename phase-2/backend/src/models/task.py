from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid
from .user import User


class TaskBase(SQLModel):
    """Base model for task with common fields"""
    title: str = Field(sa_column_kwargs={"nullable": False})
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", sa_column_kwargs={"nullable": False})


class Task(TaskBase, table=True):
    """Task model for database table"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = Field(default=None)


class TaskRead(TaskBase):
    """Schema for reading task data"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    title: str
    description: Optional[str] = None
    completed: bool = False
    user_id: Optional[uuid.UUID] = None  # This will be set from the authenticated user context
    due_date: Optional[datetime] = None


class TaskUpdate(SQLModel):
    """Schema for updating task data"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskPublic(TaskBase):
    """Public-facing task schema without sensitive data"""
    id: uuid.UUID
    created_at: datetime