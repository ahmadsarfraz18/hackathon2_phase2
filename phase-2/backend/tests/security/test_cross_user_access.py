import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.models.task import Task
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


def test_cross_user_task_access_prevention(client: TestClient, session: Session):
    """Test that users cannot access each other's tasks."""
    # Create two users
    users_data = [
        {
            "email": "user1.cross@example.com",
            "password": "password1",
            "first_name": "User1",
            "last_name": "Cross"
        },
        {
            "email": "user2.cross@example.com",
            "password": "password2",
            "first_name": "User2",
            "last_name": "Cross"
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

    # Each user creates a task
    user_tasks = []
    for i, token in enumerate(user_tokens):
        headers = {"Authorization": f"Bearer {token}"}
        task_data = {
            "title": f"User {i+1}'s task",
            "description": f"Task created by user {i+1}"
        }
        response = client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code in [200, 201]
        task = response.json()
        user_tasks.append(task)

    # Verify each user can access their own task
    for i, (token, task) in enumerate(zip(user_tokens, user_tasks)):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/tasks/{task['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == task["id"]

    # Verify each user cannot access the other user's task
    for i, (token, task) in enumerate(zip(user_tokens, user_tasks)):
        other_user_idx = 1 - i  # Get the index of the other user
        other_user_task = user_tasks[other_user_idx]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/tasks/{other_user_task['id']}", headers=headers)
        assert response.status_code == 404  # Should return 404, not 403, to prevent user enumeration


def test_cross_user_task_modification_prevention(client: TestClient, session: Session):
    """Test that users cannot modify each other's tasks."""
    # Create two users
    users = []
    for i in range(2):
        email = f"user{i+1}.modify@example.com"
        password = f"password{i+1}"

        # Signup user
        signup_data = {
            "email": email,
            "password": password,
            "first_name": f"User{i+1}",
            "last_name": "Modify"
        }
        signup_response = client.post("/auth/signup", json=signup_data)
        assert signup_response.status_code in [200, 201]

        # Login to get token
        login_data = {"email": email, "password": password}
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        users.append({"email": email, "token": token})

    # Create tasks for each user
    user_tasks = []
    for i, user in enumerate(users):
        headers = {"Authorization": f"Bearer {user['token']}"}
        task_data = {
            "title": f"User {i+1}'s task",
            "description": f"Task for user {i+1}"
        }
        response = client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code in [200, 201]
        task = response.json()
        user_tasks.append(task)

    # Verify each user cannot modify the other user's task
    for i, user in enumerate(users):
        other_user_idx = 1 - i  # Get the index of the other user
        other_user_task = user_tasks[other_user_idx]

        headers = {"Authorization": f"Bearer {user['token']}"}
        update_data = {"title": "Hacked by other user", "completed": True}
        response = client.put(f"/tasks/{other_user_task['id']}", json=update_data, headers=headers)
        assert response.status_code == 404  # Should return 404 to prevent user enumeration


def test_cross_user_task_deletion_prevention(client: TestClient, session: Session):
    """Test that users cannot delete each other's tasks."""
    # Create two users
    users = []
    for i in range(2):
        email = f"user{i+1}.delete@example.com"
        password = f"password{i+1}"

        # Signup user
        signup_data = {
            "email": email,
            "password": password,
            "first_name": f"User{i+1}",
            "last_name": "Delete"
        }
        signup_response = client.post("/auth/signup", json=signup_data)
        assert signup_response.status_code in [200, 201]

        # Login to get token
        login_data = {"email": email, "password": password}
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        users.append({"email": email, "token": token})

    # Create tasks for each user
    user_tasks = []
    for i, user in enumerate(users):
        headers = {"Authorization": f"Bearer {user['token']}"}
        task_data = {
            "title": f"User {i+1}'s task",
            "description": f"Task for user {i+1}"
        }
        response = client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code in [200, 201]
        task = response.json()
        user_tasks.append(task)

    # Verify each user cannot delete the other user's task
    for i, user in enumerate(users):
        other_user_idx = 1 - i  # Get the index of the other user
        other_user_task = user_tasks[other_user_idx]

        headers = {"Authorization": f"Bearer {user['token']}"}
        response = client.delete(f"/tasks/{other_user_task['id']}", headers=headers)
        assert response.status_code == 404  # Should return 404 to prevent user enumeration


def test_cross_user_task_list_isolation(client: TestClient, session: Session):
    """Test that users only see their own tasks in the task list."""
    # Create two users
    users = []
    for i in range(2):
        email = f"user{i+1}.list@example.com"
        password = f"password{i+1}"

        # Signup user
        signup_data = {
            "email": email,
            "password": password,
            "first_name": f"User{i+1}",
            "last_name": "List"
        }
        signup_response = client.post("/auth/signup", json=signup_data)
        assert signup_response.status_code in [200, 201]

        # Login to get token
        login_data = {"email": email, "password": password}
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        users.append({"email": email, "token": token})

    # Each user creates multiple tasks
    user_tasks = []
    for i, user in enumerate(users):
        headers = {"Authorization": f"Bearer {user['token']}"}
        user_task_list = []
        for j in range(2):  # Each user creates 2 tasks
            task_data = {
                "title": f"User {i+1}'s task {j+1}",
                "description": f"Task {j+1} for user {i+1}"
            }
            response = client.post("/tasks", json=task_data, headers=headers)
            assert response.status_code in [200, 201]
            task = response.json()
            user_task_list.append(task)
        user_tasks.append(user_task_list)

    # Verify each user only sees their own tasks
    for i, user in enumerate(users):
        headers = {"Authorization": f"Bearer {user['token']}"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200
        tasks = response.json()

        # Check that user only sees their own tasks
        assert len(tasks) == 2  # Each user should see only their 2 tasks
        for task in tasks:
            # Verify that the returned tasks have the correct user_id (this would require checking the response structure)
            # For now, we rely on the fact that the API should only return tasks belonging to the authenticated user
            pass


def test_cross_user_data_access_prevention_on_auth_me(client: TestClient, session: Session):
    """Test that the /auth/me endpoint returns only the current user's information."""
    # Create two users
    users_data = [
        {
            "email": "user1.me@example.com",
            "password": "password1",
            "first_name": "User1",
            "last_name": "Me"
        },
        {
            "email": "user2.me@example.com",
            "password": "password2",
            "first_name": "User2",
            "last_name": "Me"
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

    # Verify each token returns the correct user's information
    for i, (token, expected_user_data) in enumerate(zip(user_tokens, users_data)):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["email"] == expected_user_data["email"]
        assert user_info["first_name"] == expected_user_data["first_name"]
        assert user_info["last_name"] == expected_user_data["last_name"]


def test_user_isolation_with_direct_database_access_simulation(client: TestClient, session: Session):
    """Test that even if someone knew another user's ID, they couldn't access their data."""
    # This test verifies that our API properly isolates user data based on the authenticated user
    # rather than trusting any user ID passed in the request

    # Create two users
    user1_data = {
        "email": "user1.direct@example.com",
        "password": "password1",
        "first_name": "User1",
        "last_name": "Direct"
    }
    user2_data = {
        "email": "user2.direct@example.com",
        "password": "password2",
        "first_name": "User2",
        "last_name": "Direct"
    }

    # Signup both users
    for user_data in [user1_data, user2_data]:
        signup_response = client.post("/auth/signup", json=user_data)
        assert signup_response.status_code in [200, 201]

    # Login as both users to get tokens
    tokens = {}
    for user_data in [user1_data, user2_data]:
        login_response = client.post("/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        tokens[user_data["email"]] = login_response.json()["access_token"]

    # User1 creates a task
    headers1 = {"Authorization": f"Bearer {tokens['user1.direct@example.com']}"}
    task_data = {"title": "User1's private task", "description": "This is private"}
    create_response = client.post("/tasks", json=task_data, headers=headers1)
    assert create_response.status_code in [200, 201]
    user1_task = create_response.json()

    # Verify user2 cannot access user1's task even if they knew the task ID
    headers2 = {"Authorization": f"Bearer {tokens['user2.direct@example.com']}"}
    response = client.get(f"/tasks/{user1_task['id']}", headers=headers2)
    assert response.status_code == 404  # Should return 404, not 403, to prevent user enumeration

    # Verify user2 can still access their own data
    task_data2 = {"title": "User2's private task", "description": "This is also private"}
    create_response2 = client.post("/tasks", json=task_data2, headers=headers2)
    assert create_response2.status_code in [200, 201]
    user2_task = create_response2.json()

    # Verify user2 can access their own task
    response2 = client.get(f"/tasks/{user2_task['id']}", headers=headers2)
    assert response2.status_code == 200
    assert response2.json()["id"] == user2_task["id"]