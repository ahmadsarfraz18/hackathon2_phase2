"""SQLModel models package initialization."""

from .user import User
from .task import Task

# Ensure all models are imported to register them with SQLModel metadata
__all__ = ["User", "Task"]