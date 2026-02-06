from sqlmodel import SQLModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")  # No fallback - must be set in environment
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

# Create engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # For SQLite, use StaticPool and disable pooling for simplicity
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query logging
    )
else:
    # For PostgreSQL (including Neon), use standard engine
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections after 5 minutes
    )

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables():
    """
    Create database tables based on SQLModel models.
    This should be called on application startup.
    """
    SQLModel.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI endpoints.
    Ensures the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()