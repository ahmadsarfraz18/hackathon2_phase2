#!/usr/bin/env python3
"""
Test script to verify the login issue and test authentication functionality.
"""

import os
import sys
from pathlib import Path

# Add the backend src directory to the path
backend_dir = Path(__file__).parent / "backend"
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Set environment variables to ensure they're available
os.environ['BETTER_AUTH_SECRET'] = 'your-super-secret-key-here-make-it-long-and-random'
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'

from sqlmodel import Session, select
from backend.src.models.user import User, UserCreate
from backend.src.services.auth import authenticate_user
from backend.src.services.user_service import create_user, get_user_by_email
from backend.src.core.database import SessionLocal, engine, create_db_and_tables
from backend.src.core.security import create_access_token
from datetime import timedelta

def test_authentication():
    """Test the authentication functionality to identify the login issue."""
    print("Testing authentication functionality...")

    # Create database tables first
    print("Creating database tables...")
    create_db_and_tables()

    # Create a database session
    db = SessionLocal()

    try:
        # First, let's check if there are any users in the database
        statement = select(User)
        users = db.execute(statement).all()
        print(f"Found {len(users)} users in the database")

        # Create a test user if none exist
        if not users:
            print("Creating a test user...")
            test_user_data = UserCreate(
                email="test@example.com",
                password="TestPass123!",
                first_name="Test",
                last_name="User"
            )

            # This should work fine
            test_user = create_user(db, test_user_data)
            print(f"Created test user with ID: {test_user.id}")

        # Now let's test the authentication function directly
        print("\nTesting authentication function...")

        # Try to authenticate with correct credentials
        authenticated_user = authenticate_user(
            session=db,
            email="test@example.com",
            password="TestPass123!"
        )

        print(f"Authentication result: {authenticated_user}")

        if authenticated_user:
            print(f"Authentication successful! User ID: {authenticated_user.id}")
            print(f"User email: {authenticated_user.email}")
        else:
            print("Authentication failed!")

        # Let's also test the raw query to see what's returned
        print("\nTesting raw query...")
        statement = select(User).where(User.email == "test@example.com")
        raw_result = db.execute(statement).first()
        print(f"Raw query result: {raw_result}")
        print(f"Type of raw result: {type(raw_result)}")

        if raw_result:
            print(f"Raw result is a tuple: {isinstance(raw_result, tuple)}")
            if isinstance(raw_result, tuple):
                user_obj = raw_result[0]
                print(f"User object from raw result: {user_obj}")
                print(f"User email: {user_obj.email}")

        # Test authentication with incorrect password
        print("\nTesting authentication with wrong password...")
        wrong_auth = authenticate_user(
            session=db,
            email="test@example.com",
            password="wrongpassword"
        )
        print(f"Wrong password authentication result: {wrong_auth}")
        if not wrong_auth:
            print("Correctly failed authentication with wrong password")

        # Test authentication with non-existent user
        print("\nTesting authentication with non-existent user...")
        nonexistent_auth = authenticate_user(
            session=db,
            email="nonexistent@example.com",
            password="any_password"
        )
        print(f"Non-existent user authentication result: {nonexistent_auth}")
        if not nonexistent_auth:
            print("Correctly failed authentication with non-existent user")

    except Exception as e:
        print(f"Error during authentication test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_authentication()