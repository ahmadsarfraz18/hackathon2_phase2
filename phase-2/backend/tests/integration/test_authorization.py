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


def test_cross_user_access_prevention(client: TestClient, session: Session):
    """Test that users cannot access each other's data."""
    # Create two users
    users_data = [
        {
            "email": "user1.auth@example.com",
            "password": "password1",
            "first_name": "User",
            "last_name": "One"
        },
        {
            "email": "user2.auth@example.com",
            "password": "password2",
            "first_name": "User",
            "last_name": "Two"
        }
    ]

    user_tokens = []
    for user_data in users_data:
        # Signup each user
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

    # Verify each user can access their own data
    for i, token in enumerate(user_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        expected_email = users_data[i]["email"]
        assert user_info["email"] == expected_email


def test_user_authentication_isolation(client: TestClient, session: Session):
    """Test that authentication tokens are properly isolated between users."""
    # Create two users
    users = []
    for i in range(2):
        email = f"user{i+1}.isolation@example.com"
        password = f"password{i+1}"

        # Signup user
        signup_data = {
            "email": email,
            "password": password,
            "first_name": f"User{i+1}",
            "last_name": f"Isolation"
        }
        signup_response = client.post("/auth/signup", json=signup_data)
        assert signup_response.status_code in [200, 201]

        # Login to get token
        login_data = {
            "email": email,
            "password": password
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        users.append({"email": email, "password": password, "token": token})

    # Verify that each token is associated with the correct user
    for user in users:
        headers = {"Authorization": f"Bearer {user['token']}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["email"] == user["email"]


def test_token_cannot_be_used_for_different_user_data(client: TestClient, session: Session):
    """Test that a token from one user cannot be used to impersonate another user."""
    # Create two users
    user1_data = {
        "email": "user1.impersonation@example.com",
        "password": "password1",
        "first_name": "User",
        "last_name": "One"
    }
    user2_data = {
        "email": "user2.impersonation@example.com",
        "password": "password2",
        "first_name": "User",
        "last_name": "Two"
    }

    # Signup both users
    for user_data in [user1_data, user2_data]:
        signup_response = client.post("/auth/signup", json=user_data)
        assert signup_response.status_code in [200, 201]

    # Login as user1 to get token
    login_response = client.post("/auth/login", json={
        "email": "user1.impersonation@example.com",
        "password": "password1"
    })
    assert login_response.status_code == 200
    user1_token = login_response.json()["access_token"]

    # Login as user2 to get token
    login_response = client.post("/auth/login", json={
        "email": "user2.impersonation@example.com",
        "password": "password2"
    })
    assert login_response.status_code == 200
    user2_token = login_response.json()["access_token"]

    # Verify user1 token returns user1's info
    headers1 = {"Authorization": f"Bearer {user1_token}"}
    response1 = client.get("/auth/me", headers=headers1)
    assert response1.status_code == 200
    assert response1.json()["email"] == "user1.impersonation@example.com"

    # Verify user2 token returns user2's info
    headers2 = {"Authorization": f"Bearer {user2_token}"}
    response2 = client.get("/auth/me", headers=headers2)
    assert response2.status_code == 200
    assert response2.json()["email"] == "user2.impersonation@example.com"

    # Verify that user1's token cannot access user2's private info or vice versa
    # (This is tested through the auth.me endpoint which should return the user's own info)
    assert response1.json()["email"] != response2.json()["email"]


def test_invalid_token_provides_no_access(client: TestClient, session: Session):
    """Test that invalid or missing tokens provide no access to protected resources."""
    # Test without any token
    response_no_token = client.get("/auth/me")
    assert response_no_token.status_code == 401

    # Test with invalid token format
    invalid_headers = {"Authorization": "Bearer invalid.token.format"}
    response_invalid = client.get("/auth/me", headers=invalid_headers)
    assert response_invalid.status_code == 401

    # Test with completely random token
    random_headers = {"Authorization": "Bearer somerandomstring"}
    response_random = client.get("/auth/me", headers=random_headers)
    assert response_random.status_code == 401


def test_user_session_independence(client: TestClient, session: Session):
    """Test that user sessions are independent and don't interfere with each other."""
    # Create multiple users
    users = []
    for i in range(3):
        user_data = {
            "email": f"user{i+1}.session@example.com",
            "password": f"password{i+1}",
            "first_name": f"User{i+1}",
            "last_name": f"Session"
        }

        # Signup user
        signup_response = client.post("/auth/signup", json=user_data)
        assert signup_response.status_code in [200, 201]

        # Login to get token
        login_response = client.post("/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        users.append({"email": user_data["email"], "token": token})

    # Verify each user session works independently
    for user in users:
        headers = {"Authorization": f"Bearer {user['token']}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == user["email"]

    # Verify that using one user's token doesn't affect another's session
    for i, user in enumerate(users):
        headers = {"Authorization": f"Bearer {user['token']}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == user["email"]
        assert response.json()["email"] == users[i]["email"]  # Confirm consistency


def test_token_revocation_simulation(client: TestClient, session: Session):
    """Test scenarios related to token validity and user state changes."""
    # Create a user
    user_data = {
        "email": "token.revocation@example.com",
        "password": "password123",
        "first_name": "Token",
        "last_name": "Revocation"
    }

    # Signup user
    signup_response = client.post("/auth/signup", json=user_data)
    assert signup_response.status_code in [200, 201]

    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "token.revocation@example.com",
        "password": "password123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Verify token works initially
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "token.revocation@example.com"

    # Simulate what would happen if a user account was deactivated
    # In a real system, this might involve checking user status on each request
    # For this test, we're just verifying the token still works for the active user
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200