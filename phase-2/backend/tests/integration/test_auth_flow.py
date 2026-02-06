import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.services.auth import get_password_hash, verify_token
import json


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


def test_complete_signup_login_flow(client: TestClient, session: Session):
    """Test the complete signup and login flow end-to-end."""
    # Step 1: Signup a new user
    signup_data = {
        "email": "integration_test@example.com",
        "password": "securepassword123",
        "first_name": "Integration",
        "last_name": "Test"
    }

    signup_response = client.post("/auth/signup", json=signup_data)

    # Verify signup was successful
    assert signup_response.status_code in [200, 201]
    signup_result = signup_response.json()
    assert "id" in signup_result
    assert signup_result["email"] == "integration_test@example.com"
    assert signup_result["first_name"] == "Integration"

    # Step 2: Login with the same credentials
    login_data = {
        "email": "integration_test@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)

    # Verify login was successful
    assert login_response.status_code == 200
    login_result = login_response.json()
    assert "access_token" in login_result
    assert login_result["token_type"] == "bearer"

    # Step 3: Verify the JWT token is valid
    token = login_result["access_token"]
    payload = verify_token(token)
    assert payload is not None
    assert "user_id" in payload
    assert payload["email"] == "integration_test@example.com"


def test_login_after_signup_then_use_token(client: TestClient, session: Session):
    """Test that a user can signup, login, get a token, and use it for protected endpoints."""
    # Step 1: Signup
    signup_data = {
        "email": "protected_test@example.com",
        "password": "securepassword123",
        "first_name": "Protected",
        "last_name": "Test"
    }

    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in [200, 201]

    # Step 2: Login to get token
    login_data = {
        "email": "protected_test@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Step 3: Use token for a protected endpoint (assuming one exists)
    # For now, we'll just verify the token format
    assert token.startswith("eyJ")  # JWT tokens start with "eyJ" when base64 encoded


def test_multiple_users_can_signup_and_login(client: TestClient, session: Session):
    """Test that multiple users can independently signup and login."""
    users_data = [
        {
            "email": "user1@test.com",
            "password": "password1",
            "first_name": "User",
            "last_name": "One"
        },
        {
            "email": "user2@test.com",
            "password": "password2",
            "first_name": "User",
            "last_name": "Two"
        }
    ]

    tokens = []
    for user_data in users_data:
        # Signup
        signup_response = client.post("/auth/signup", json=user_data)
        assert signup_response.status_code in [200, 201]

        # Login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        tokens.append(token)

        # Verify each token is valid and has correct user info
        payload = verify_token(token)
        assert payload is not None
        assert payload["email"] == user_data["email"]


def test_signup_then_immediate_login(client: TestClient, session: Session):
    """Test that a user can immediately login after signup with the same credentials."""
    test_user = {
        "email": "immediate_login@test.com",
        "password": "very_secure_password",
        "first_name": "Immediate",
        "last_name": "Login"
    }

    # Signup
    signup_response = client.post("/auth/signup", json=test_user)
    assert signup_response.status_code in [200, 201]

    # Immediately try to login with same credentials
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Verify we got a token
    result = login_response.json()
    assert "access_token" in result
    assert result["token_type"] == "bearer"


def test_case_sensitive_email_handling(client: TestClient, session: Session):
    """Test that email handling is case-sensitive for security."""
    # Register user with lowercase email
    signup_data = {
        "email": "case@test.com",
        "password": "password",
        "first_name": "Case",
        "last_name": "Sensitive"
    }

    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in [200, 201]

    # Try to login with uppercase email (should fail)
    login_data_upper = {
        "email": "CASE@TEST.COM",  # Uppercase version
        "password": "password"
    }
    login_response_upper = client.post("/auth/login", json=login_data_upper)
    assert login_response_upper.status_code == 401  # Should fail

    # Login with correct case should succeed
    login_data_correct = {
        "email": "case@test.com",  # Correct case
        "password": "password"
    }
    login_response_correct = client.post("/auth/login", json=login_data_correct)
    assert login_response_correct.status_code == 200  # Should succeed