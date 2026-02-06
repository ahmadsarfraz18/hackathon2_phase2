#!/usr/bin/env python3
"""
Script to initialize the database with all required tables for Neon DB.
"""

import asyncio
from sqlmodel import SQLModel
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from src.models.user import User
from src.models.task import Task

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

print(f"Connecting to database: {DATABASE_URL}")

# Create engine for PostgreSQL (Neon)
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Enable logging to see what's happening
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections after 5 minutes
)

def create_db_and_tables():
    """Create database tables based on SQLModel models."""
    print("Creating database tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_db_and_tables()
    print("Database initialization completed!")