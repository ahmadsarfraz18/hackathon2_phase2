from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TimestampMixin:
    """Mixin class to add timestamp fields to models"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


def create_engine_and_session(database_url: Optional[str] = None):
    """
    Create database engine and sessionmaker.

    Args:
        database_url: Database connection string. If None, will try to get from environment.

    Returns:
        Tuple of (engine, sessionmaker)
    """
    import os

    if not database_url:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal


def get_session():
    """
    Dependency to get database session.
    """
    from .base import create_engine_and_session
    _, SessionLocal = create_engine_and_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()