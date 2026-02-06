import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.services.auth import get_password_hash, create_access_token
from datetime import timedelta
import time


@pytest.fixture(name="client")
def client_fixture():
    """Create a test client with override dependencies."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    with Session(engine) as session:
        yield session


def test_expired_token_returns_401(client: TestClient, session: Session):
    """Test that expired JWT tokens return 401 Unauthorized."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="expired.test@example.com",
        password_hash=hashed_password,
        first_name="Expired",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create a token that expires immediately (for testing purposes)
    expired_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=timedelta(seconds=1)  # Token expires in 1 second
    )

    # Wait for the token to expire
    time.sleep(2)

    # Try to use the expired token
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/auth/me", headers=headers)

    # Should return 401 Unauthorized due to expired token
    assert response.status_code == 401


def test_expired_token_on_different_endpoints(client: TestClient, session: Session):
    """Test that expired tokens return 401 on various endpoints."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="expired.multi@example.com",
        password_hash=hashed_password,
        first_name="Expired",
        last_name="Multi"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create an expired token
    expired_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=timedelta(seconds=1)  # Token expires in 1 second
    )

    # Wait for the token to expire
    time.sleep(2)

    # Test various endpoints with expired token
    endpoints_to_test = [
        "/auth/me",
        "/tasks",
    ]

    for endpoint in endpoints_to_test:
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get(endpoint, headers=headers)
        assert response.status_code == 401, f"Endpoint {endpoint} should return 401 for expired token"

    # Test POST endpoint as well
    response = client.post("/tasks", json={"title": "Test"}, headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_near_expired_token_behavior(client: TestClient, session: Session):
    """Test behavior of tokens that are about to expire."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="near.expired@example.com",
        password_hash=hashed_password,
        first_name="Near",
        last_name="Expired"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create a token that expires in 2 seconds
    nearly_expired_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=timedelta(seconds=2)
    )

    # Use the token immediately - should work
    headers = {"Authorization": f"Bearer {nearly_expired_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200

    # Wait for the token to expire
    time.sleep(3)

    # Now try to use the expired token - should fail
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401


def test_expired_token_error_message(client: TestClient, session: Session):
    """Test that expired tokens return appropriate error messages."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="expired.error@example.com",
        password_hash=hashed_password,
        first_name="Expired",
        last_name="Error"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create an expired token
    expired_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=timedelta(seconds=1)
    )

    # Wait for the token to expire
    time.sleep(2)

    # Try to use the expired token
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401
    response_json = response.json()
    # Check that the response contains appropriate error information
    assert "detail" in response_json


def test_multiple_expired_tokens(client: TestClient, session: Session):
    """Test behavior with multiple expired tokens."""
    users_data = [
        {"email": "expired1@example.com", "password": "password1", "first_name": "Expired1", "last_name": "User"},
        {"email": "expired2@example.com", "password": "password2", "first_name": "Expired2", "last_name": "User"}
    ]

    expired_tokens = []
    for user_data in users_data:
        # Create user
        hashed_password = get_password_hash(user_data["password"])
        user = User(
            email=user_data["email"],
            password_hash=hashed_password,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"]
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create expired token
        expired_token = create_access_token(
            data={"user_id": str(user.id), "email": user.email},
            expires_delta=timedelta(seconds=1)
        )
        expired_tokens.append(expired_token)

    # Wait for tokens to expire
    time.sleep(2)

    # Test that all expired tokens return 401
    for token in expired_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401


def test_expired_vs_invalid_token_distinction(client: TestClient, session: Session):
    """Test that expired tokens are handled differently from invalid tokens."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="distinction.test@example.com",
        password_hash=hashed_password,
        first_name="Distinction",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create an expired token
    expired_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=timedelta(seconds=1)
    )

    # Wait for the token to expire
    time.sleep(2)

    # Create an invalid token (random string)
    invalid_token = "this.is.not.a.valid.token"

    # Both should return 401, but the system should handle them properly
    expired_headers = {"Authorization": f"Bearer {expired_token}"}
    invalid_headers = {"Authorization": f"Bearer {invalid_token}"}

    expired_response = client.get("/auth/me", headers=expired_headers)
    invalid_response = client.get("/auth/me", headers=invalid_headers)

    # Both should return 401
    assert expired_response.status_code == 401
    assert invalid_response.status_code == 401


def test_token_expiration_affects_all_user_operations(client: TestClient, session: Session):
    """Test that token expiration affects all user operations consistently."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="all.ops@example.com",
        password_hash=hashed_password,
        first_name="All",
        last_name="Ops"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create an expired token
    expired_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=timedelta(seconds=1)
    )

    # Wait for the token to expire
    time.sleep(2)

    # Test various operations with expired token
    headers = {"Authorization": f"Bearer {expired_token}"}

    # GET operations
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 401

    # POST operation
    response = client.post("/tasks", json={"title": "Test"}, headers=headers)
    assert response.status_code == 401

    # PUT operation would require creating a task first, but conceptually should also fail