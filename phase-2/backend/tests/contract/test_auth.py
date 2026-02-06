import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.services.auth import get_password_hash


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


def test_signup_endpoint_contract(client: TestClient, session: Session):
    """Test the signup endpoint contract - valid request structure and response format."""
    # Prepare valid signup data
    signup_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User"
    }

    # Send signup request
    response = client.post("/auth/signup", json=signup_data)

    # Assert response structure and status
    assert response.status_code in [200, 201]  # Success codes
    assert "id" in response.json()
    assert "email" in response.json()
    assert "created_at" in response.json()


def test_login_endpoint_contract(client: TestClient, session: Session):
    """Test the login endpoint contract - valid request structure and response format."""
    # First create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="login@example.com",
        password_hash=hashed_password,
        first_name="Login",
        last_name="User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Prepare valid login data
    login_data = {
        "email": "login@example.com",
        "password": "securepassword123"
    }

    # Send login request
    response = client.post("/auth/login", json=login_data)

    # Assert response structure and status
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_invalid_credentials_login(client: TestClient, session: Session):
    """Test login with invalid credentials returns appropriate error."""
    # Prepare invalid login data
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }

    # Send login request
    response = client.post("/auth/login", json=login_data)

    # Assert appropriate error response
    assert response.status_code == 401
    assert "detail" in response.json()


def test_signup_duplicate_email(client: TestClient, session: Session):
    """Test signup with duplicate email returns appropriate error."""
    # First create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="duplicate@example.com",
        password_hash=hashed_password,
        first_name="Duplicate",
        last_name="User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Prepare signup data with duplicate email
    signup_data = {
        "email": "duplicate@example.com",  # Same email as above
        "password": "anotherpassword",
        "first_name": "Another",
        "last_name": "User"
    }

    # Send signup request
    response = client.post("/auth/signup", json=signup_data)

    # Assert appropriate error response for duplicate email
    assert response.status_code in [400, 409]  # Bad request or conflict


def test_signup_missing_fields(client: TestClient):
    """Test signup with missing required fields returns appropriate error."""
    # Prepare signup data with missing fields
    signup_data = {
        "email": "test@example.com"
        # Missing password field
    }

    # Send signup request
    response = client.post("/auth/signup", json=signup_data)

    # Assert appropriate error response for missing fields
    assert response.status_code == 422  # Unprocessable entity


def test_login_missing_fields(client: TestClient):
    """Test login with missing required fields returns appropriate error."""
    # Prepare login data with missing fields
    login_data = {
        "email": "test@example.com"
        # Missing password field
    }

    # Send login request
    response = client.post("/auth/login", json=login_data)

    # Assert appropriate error response for missing fields
    assert response.status_code == 422  # Unprocessable entity