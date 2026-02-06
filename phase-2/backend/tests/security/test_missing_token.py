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


def test_protected_endpoint_without_token_returns_401(client: TestClient, session: Session):
    """Test that protected endpoints return 401 when no token is provided."""
    # Test auth/me endpoint without token
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()

    # Test task endpoints without token
    response = client.get("/tasks")
    assert response.status_code == 401
    assert "detail" in response.json()

    response = client.post("/tasks", json={"title": "Test task", "user_id": "some-id"})
    assert response.status_code == 401
    assert "detail" in response.json()


def test_protected_endpoints_return_401_without_auth_header(client: TestClient, session: Session):
    """Test that protected endpoints return 401 when Authorization header is missing."""
    # Create headers without Authorization
    headers = {"Content-Type": "application/json"}

    # Test endpoints without auth header
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 401

    response = client.post("/tasks", json={"title": "Test task"}, headers=headers)
    assert response.status_code == 401


def test_protected_endpoints_return_401_with_empty_auth_header(client: TestClient, session: Session):
    """Test that protected endpoints return 401 when Authorization header is empty."""
    # Create headers with empty Authorization
    headers = {"Authorization": "", "Content-Type": "application/json"}

    # Test endpoints with empty auth header
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 401


def test_auth_endpoint_access_without_token(client: TestClient, session: Session):
    """Test that authentication-related endpoints behave appropriately without tokens."""
    # Signup endpoint should not require authentication
    signup_data = {
        "email": "no.token@example.com",
        "password": "securepassword123",
        "first_name": "No",
        "last_name": "Token"
    }
    response = client.post("/auth/signup", json=signup_data)
    # This might succeed or fail based on if user already exists, but shouldn't be 401
    assert response.status_code in [200, 201, 409]  # OK, Created, or Conflict (if user exists)


def test_behavior_of_different_endpoint_types(client: TestClient, session: Session):
    """Test that different endpoint types behave correctly regarding authentication."""
    # Public endpoints (like health check) should not require auth
    response = client.get("/health")
    assert response.status_code == 200

    # Protected endpoints should require auth
    protected_endpoints = [
        "/auth/me",
        "/tasks",
    ]

    for endpoint in protected_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

    # Test protected POST endpoints
    protected_post_endpoints = [
        "/tasks",
    ]

    for endpoint in protected_post_endpoints:
        response = client.post(endpoint, json={"title": "test"})
        assert response.status_code == 401, f"POST to {endpoint} should require authentication"


def test_multiple_protected_endpoints_without_token(client: TestClient, session: Session):
    """Test multiple protected endpoints to ensure consistent 401 behavior."""
    # Create a user to ensure the endpoints exist and work with proper auth
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="multi.test@example.com",
        password_hash=hashed_password,
        first_name="Multi",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to verify the endpoints exist and work with proper auth
    login_data = {
        "email": "multi.test@example.com",
        "password": "securepassword123"
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Verify that with proper auth, endpoints work
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200

    # Now test without auth
    response = client.get("/auth/me")
    assert response.status_code == 401

    response = client.get("/tasks")
    assert response.status_code == 401

    response = client.post("/tasks", json={"title": "Test"})
    assert response.status_code == 401


def test_correct_error_message_for_missing_token(client: TestClient):
    """Test that the correct error message is returned for missing tokens."""
    response = client.get("/auth/me")
    assert response.status_code == 401

    response_json = response.json()
    # Check that the response contains appropriate error information
    assert "detail" in response_json or "error" in response_json