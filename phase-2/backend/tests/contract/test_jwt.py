import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.services.auth import get_password_hash
from backend.src.api.deps import verify_token_payload
import jwt
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


def test_jwt_token_structure(client: TestClient, session: Session):
    """Test that JWT tokens have the correct structure and claims."""
    # First create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="jwt.test@example.com",
        password_hash=hashed_password,
        first_name="JWT",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "jwt.test@example.com",
        "password": "securepassword123"
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    result = response.json()
    assert "access_token" in result
    assert result["token_type"] == "bearer"

    token = result["access_token"]

    # Verify the token structure manually by decoding
    secret = os.getenv("BETTER_AUTH_SECRET", "")
    assert secret, "BETTER_AUTH_SECRET must be set for JWT testing"

    # Decode the token without verification to check structure
    decoded = jwt.decode(token, options={"verify_signature": False})

    # Verify required claims are present
    assert "user_id" in decoded, "Token must contain user_id claim"
    assert "email" in decoded, "Token must contain email claim"
    assert "exp" in decoded, "Token must contain exp claim"


def test_jwt_token_contains_correct_user_info(client: TestClient, session: Session):
    """Test that JWT tokens contain the correct user information."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="correct.info@example.com",
        password_hash=hashed_password,
        first_name="Correct",
        last_name="Info"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "correct.info@example.com",
        "password": "securepassword123"
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    result = response.json()
    token = result["access_token"]

    # Decode the token to check user info
    secret = os.getenv("BETTER_AUTH_SECRET", "")
    decoded = jwt.decode(token, options={"verify_signature": False})

    # Verify user-specific claims
    assert decoded["user_id"] == str(user.id)
    assert decoded["email"] == "correct.info@example.com"


def test_jwt_token_expiration(client: TestClient, session: Session):
    """Test that JWT tokens have proper expiration."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="exp.test@example.com",
        password_hash=hashed_password,
        first_name="Expiration",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "exp.test@example.com",
        "password": "securepassword123"
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    result = response.json()
    token = result["access_token"]

    # Decode the token to check expiration
    secret = os.getenv("BETTER_AUTH_SECRET", "")
    decoded = jwt.decode(token, options={"verify_signature": False})

    # Verify expiration claim exists and is in the future
    assert "exp" in decoded
    import time
    assert decoded["exp"] > time.time(), "Token expiration should be in the future"


def test_jwt_token_verification(client: TestClient, session: Session):
    """Test that JWT tokens can be properly verified by the system."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="verify.test@example.com",
        password_hash=hashed_password,
        first_name="Verify",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "verify.test@example.com",
        "password": "securepassword123"
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    result = response.json()
    token = result["access_token"]

    # Test that the token can be verified by the system's verification function
    # This simulates how protected endpoints would verify the token
    from backend.src.services.auth import verify_token
    payload = verify_token(token)
    assert payload is not None, "Token should be verifiable by the system"
    assert payload["user_id"] == str(user.id)
    assert payload["email"] == "verify.test@example.com"


def test_invalid_jwt_rejection(client: TestClient):
    """Test that invalid JWT tokens are properly rejected."""
    # Try to access a protected endpoint with an invalid token
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/auth/me", headers=headers)

    # Should return 401 Unauthorized
    assert response.status_code == 401


def test_malformed_jwt_rejection(client: TestClient):
    """Test that malformed JWT tokens are properly rejected."""
    # Try to access a protected endpoint with a malformed token
    headers = {"Authorization": "Bearer malformed"}
    response = client.get("/auth/me", headers=headers)

    # Should return 401 Unauthorized
    assert response.status_code == 401