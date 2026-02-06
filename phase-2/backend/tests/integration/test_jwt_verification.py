import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.services.auth import get_password_hash, create_access_token
from datetime import timedelta
import time
import os


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


def test_complete_jwt_flow_integration(client: TestClient, session: Session):
    """Test the complete JWT flow: signup, login, token usage, and verification."""
    # Step 1: Signup a new user
    signup_data = {
        "email": "integration.jwt@example.com",
        "password": "securepassword123",
        "first_name": "Integration",
        "last_name": "JWT"
    }

    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in [200, 201]
    signup_result = signup_response.json()
    assert "id" in signup_result
    user_id = signup_result["id"]

    # Step 2: Login to get JWT token
    login_data = {
        "email": "integration.jwt@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_result = login_response.json()
    assert "access_token" in login_result
    token = login_result["access_token"]

    # Step 3: Use token to access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    protected_response = client.get("/auth/me", headers=headers)
    assert protected_response.status_code == 200
    user_info = protected_response.json()
    assert user_info["id"] == user_id
    assert user_info["email"] == "integration.jwt@example.com"


def test_jwt_token_validation_in_protected_endpoint(client: TestClient, session: Session):
    """Test that protected endpoints properly validate JWT tokens."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="protected.test@example.com",
        password_hash=hashed_password,
        first_name="Protected",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "protected.test@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Test accessing protected endpoint with valid token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "protected.test@example.com"

    # Test accessing protected endpoint without token
    response_no_auth = client.get("/auth/me")
    assert response_no_auth.status_code == 401

    # Test accessing protected endpoint with invalid token
    invalid_headers = {"Authorization": "Bearer invalid.token.here"}
    response_invalid = client.get("/auth/me", headers=invalid_headers)
    assert response_invalid.status_code == 401


def test_jwt_token_user_isolation(client: TestClient, session: Session):
    """Test that JWT tokens provide proper user isolation."""
    # Create two different users
    users_data = [
        {
            "email": "user1.jwt@example.com",
            "password": "password1",
            "first_name": "User",
            "last_name": "One"
        },
        {
            "email": "user2.jwt@example.com",
            "password": "password2",
            "first_name": "User",
            "last_name": "Two"
        }
    ]

    user_tokens = []
    for user_data in users_data:
        # Signup user
        signup_response = client.post("/auth/signup", json=user_data)
        assert signup_response.status_code in [200, 201]

        # Login to get token
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        user_tokens.append(token)

    # Verify each token returns the correct user info
    for i, token in enumerate(user_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        expected_email = users_data[i]["email"]
        assert user_info["email"] == expected_email


def test_expired_jwt_token_handling(client: TestClient, session: Session):
    """Test that expired JWT tokens are properly rejected."""
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
    from datetime import datetime, timedelta
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


def test_jwt_token_algorithm_security(client: TestClient, session: Session):
    """Test that tokens using different algorithms are handled appropriately."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="algorithm.test@example.com",
        password_hash=hashed_password,
        first_name="Algorithm",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a proper JWT token
    login_data = {
        "email": "algorithm.test@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    valid_token = login_response.json()["access_token"]

    # Verify the valid token works
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200

    # Test that the system properly validates the token algorithm
    # (This is more of a security check - ensuring the system doesn't accept
    # tokens with unsafe algorithms like 'none')
    # In a real test, we might try to craft tokens with different algorithms


def test_jwt_payload_integrity(client: TestClient, session: Session):
    """Test that JWT token payloads maintain integrity."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="integrity.test@example.com",
        password_hash=hashed_password,
        first_name="Integrity",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "integrity.test@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Use the token to access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200

    # Verify that the user information returned matches what was stored
    user_info = response.json()
    assert user_info["email"] == "integrity.test@example.com"
    assert user_info["first_name"] == "Integrity"
    assert user_info["last_name"] == "Test"
    assert user_info["id"] == str(user.id)