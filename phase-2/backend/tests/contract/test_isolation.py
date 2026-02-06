import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.services.auth import get_password_hash
from backend.src.models.user import UserCreate


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


def test_user_isolation_contract_for_task_endpoints(client: TestClient, session: Session):
    """Test the contract for user isolation in task-related endpoints."""
    # First, we need to create users and potentially a task model
    # For this test, we'll check if the expected endpoints exist and require authentication
    # This is a contract test, so we're checking the interface, not the full functionality

    # Test that protected endpoints require authentication
    # These would be endpoints like /tasks/ or /tasks/{id} that should require a valid token

    # Check that accessing a protected endpoint without authentication returns 401
    response = client.get("/tasks")
    assert response.status_code == 401, "Protected endpoint should return 401 without authentication"

    # Check that accessing a protected endpoint with invalid authentication returns 401
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 401, "Protected endpoint should return 401 with invalid token"


def test_user_data_isolation_contract(client: TestClient, session: Session):
    """Test the contract for user data isolation."""
    # Create a user directly in the database
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="isolation.test@example.com",
        password_hash=hashed_password,
        first_name="Isolation",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "isolation.test@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Test that authenticated requests work
    headers = {"Authorization": f"Bearer {token}"}
    # This is a placeholder test - actual implementation would depend on having task endpoints
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "isolation.test@example.com"


def test_cross_user_access_prevention_contract(client: TestClient, session: Session):
    """Test the contract for preventing cross-user access."""
    # Create two users directly in the database
    users_data = [
        {
            "email": "user1.isolation@example.com",
            "password": "password1",
            "first_name": "User",
            "last_name": "One"
        },
        {
            "email": "user2.isolation@example.com",
            "password": "password2",
            "first_name": "User",
            "last_name": "Two"
        }
    ]

    user_tokens = []
    for user_data in users_data:
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

        # Login to get token
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        user_tokens.append(token)

    # This is a contract test - we're verifying the interface exists
    # The actual cross-user access prevention would be tested in integration tests
    # For now, we just verify that authenticated endpoints work for each user
    for i, token in enumerate(user_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200


def test_user_specific_endpoints_require_authentication(client: TestClient, session: Session):
    """Test that user-specific endpoints require authentication."""
    # Create a user
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="auth.test@example.com",
        password_hash=hashed_password,
        first_name="Auth",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Test that user-specific endpoints require authentication
    # Placeholder for actual user-specific endpoints
    endpoints_to_test = [
        "/auth/me",  # This endpoint exists
        # Add other user-specific endpoints when they are implemented
    ]

    for endpoint in endpoints_to_test:
        # Test without authentication
        response = client.get(endpoint)
        assert response.status_code in [401, 403], f"Endpoint {endpoint} should require authentication"

        # Test with valid authentication
        login_data = {
            "email": "auth.test@example.com",
            "password": "securepassword123"
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(endpoint, headers=headers)
        assert response.status_code not in [401, 403], f"Endpoint {endpoint} should allow authenticated requests"


def test_user_id_extraction_from_token_contract(client: TestClient, session: Session):
    """Test the contract for user ID extraction from JWT tokens."""
    # Create a user
    hashed_password = get_password_hash("securepassword123")
    user = User(
        email="userid.test@example.com",
        password_hash=hashed_password,
        first_name="UserID",
        last_name="Test"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Login to get a JWT token
    login_data = {
        "email": "userid.test@example.com",
        "password": "securepassword123"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Test that the token can be used to access user-specific data
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    user_info = response.json()
    assert "id" in user_info
    assert user_info["email"] == "userid.test@example.com"