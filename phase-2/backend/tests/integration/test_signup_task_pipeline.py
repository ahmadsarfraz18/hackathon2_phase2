"""
End-to-end test pipeline for user signup followed by task creation and management.

This test suite validates the complete user journey from signup through task creation,
ensuring the proper integration of authentication, user management, and task management
components.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from backend.src.main import app
from backend.src.core.database import get_db, engine
from backend.src.models.user import User
from backend.src.models.task import Task
from backend.src.services.auth import verify_token


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


def test_complete_signup_task_creation_pipeline(client: TestClient, session: Session):
    """
    Test the complete pipeline: signup -> login -> create task -> verify task exists.

    This test validates the entire user onboarding flow with task creation.
    """
    # Step 1: Signup a new user
    signup_data = {
        "email": "pipeline_test@example.com",
        "password": "SecurePass123!",
        "first_name": "Pipeline",
        "last_name": "Test"
    }

    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in [200, 201], f"Signup failed: {signup_response.text}"

    signup_result = signup_response.json()
    assert "id" in signup_result
    assert signup_result["email"] == "pipeline_test@example.com"
    assert signup_result["first_name"] == "Pipeline"
    assert signup_result["last_name"] == "Test"
    print(f"✓ User signed up successfully with ID: {signup_result['id']}")

    # Step 2: Login with the created credentials to get an access token
    login_data = {
        "email": "pipeline_test@example.com",
        "password": "SecurePass123!"
    }

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    login_result = login_response.json()
    assert "access_token" in login_result
    assert login_result["token_type"] == "bearer"
    token = login_result["access_token"]
    print("✓ User logged in successfully, received access token")

    # Step 3: Verify the JWT token is valid and contains correct user information
    payload = verify_token(token)
    assert payload is not None, "Invalid JWT token"
    assert "user_id" in payload
    assert payload["email"] == "pipeline_test@example.com"
    print("✓ JWT token validated successfully")

    # Step 4: Create a task using the authenticated user's token
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Welcome Task",
        "description": "This task was created after successful signup and login",
        "completed": False
    }

    create_task_response = client.post("/tasks", json=task_data, headers=headers)
    assert create_task_response.status_code in [200, 201], f"Task creation failed: {create_task_response.text}"

    created_task = create_task_response.json()
    assert "id" in created_task
    assert created_task["title"] == "Welcome Task"
    assert created_task["description"] == "This task was created after successful signup and login"
    assert created_task["completed"] is False
    assert created_task["user_id"] == signup_result["id"]  # Verify task is linked to user
    print(f"✓ Task created successfully with ID: {created_task['id']}")

    # Step 5: Retrieve the created task to verify it was saved correctly
    get_task_response = client.get(f"/tasks/{created_task['id']}", headers=headers)
    assert get_task_response.status_code == 200

    retrieved_task = get_task_response.json()
    assert retrieved_task["id"] == created_task["id"]
    assert retrieved_task["title"] == created_task["title"]
    assert retrieved_task["description"] == created_task["description"]
    assert retrieved_task["completed"] == created_task["completed"]
    print("✓ Created task retrieved successfully and matches original data")

    # Step 6: Verify the task appears in the user's task list
    get_all_tasks_response = client.get("/tasks", headers=headers)
    assert get_all_tasks_response.status_code == 200

    all_tasks = get_all_tasks_response.json()
    assert len(all_tasks) >= 1  # May have other tasks from other tests
    user_task_exists = any(task["id"] == created_task["id"] for task in all_tasks)
    assert user_task_exists, "Created task not found in user's task list"
    print("✓ Task appears in user's task list")


def test_signup_multiple_tasks_pipeline(client: TestClient, session: Session):
    """
    Test the pipeline with multiple task creation after signup.

    Validates that a user can create multiple tasks after signing up.
    """
    # Step 1: Signup a new user
    signup_data = {
        "email": "multi_task_test@example.com",
        "password": "SecurePass456!",
        "first_name": "Multi",
        "last_name": "Task"
    }

    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in [200, 201]

    signup_result = signup_response.json()
    user_id = signup_result["id"]
    assert signup_result["email"] == "multi_task_test@example.com"
    print(f"✓ User signed up successfully with ID: {user_id}")

    # Step 2: Login to get token
    login_response = client.post("/auth/login", json={
        "email": "multi_task_test@example.com",
        "password": "SecurePass456!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ User logged in successfully")

    # Step 3: Create multiple tasks
    tasks_to_create = [
        {"title": "First Task", "description": "Initial task after signup"},
        {"title": "Second Task", "description": "Additional task"},
        {"title": "Third Task", "description": "Final task in sequence"}
    ]

    created_tasks = []
    for i, task_data in enumerate(tasks_to_create):
        task_response = client.post("/tasks", json=task_data, headers=headers)
        assert task_response.status_code in [200, 201]

        task = task_response.json()
        assert task["title"] == task_data["title"]
        assert task["description"] == task_data["description"]
        assert task["user_id"] == user_id  # Verify task belongs to correct user
        created_tasks.append(task)
        print(f"✓ Task {i+1} created successfully: {task['title']}")

    # Step 4: Verify all tasks exist and belong to the user
    all_tasks_response = client.get("/tasks", headers=headers)
    assert all_tasks_response.status_code == 200

    all_tasks = all_tasks_response.json()
    user_tasks = [task for task in all_tasks if task["user_id"] == user_id]
    assert len(user_tasks) >= 3  # At least the 3 tasks we created

    # Verify our created tasks are in the list
    created_task_ids = {task["id"] for task in created_tasks}
    returned_task_ids = {task["id"] for task in user_tasks}
    assert created_task_ids.issubset(returned_task_ids), "Not all created tasks were returned"
    print(f"✓ All {len(created_tasks)} tasks verified in user's task list")


def test_signup_task_update_delete_pipeline(client: TestClient, session: Session):
    """
    Test the complete pipeline including task updates and deletion after signup.

    Validates the full CRUD cycle for tasks after user signup.
    """
    # Step 1: Signup a new user
    signup_data = {
        "email": "crud_pipeline_test@example.com",
        "password": "SecurePass789!",
        "first_name": "CRUD",
        "last_name": "Pipeline"
    }

    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in [200, 201]
    user_data = signup_response.json()
    assert user_data["email"] == "crud_pipeline_test@example.com"
    print(f"✓ User signed up successfully with ID: {user_data['id']}")

    # Step 2: Login to get token
    login_response = client.post("/auth/login", json={
        "email": "crud_pipeline_test@example.com",
        "password": "SecurePass789!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ User logged in successfully")

    # Step 3: Create a task
    task_data = {
        "title": "Original Task Title",
        "description": "Original task description",
        "completed": False
    }

    create_response = client.post("/tasks", json=task_data, headers=headers)
    assert create_response.status_code in [200, 201]
    task = create_response.json()
    original_task_id = task["id"]
    print(f"✓ Task created successfully with ID: {original_task_id}")

    # Step 4: Update the task
    update_data = {
        "title": "Updated Task Title",
        "description": "Updated task description",
        "completed": True
    }

    update_response = client.put(f"/tasks/{original_task_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated Task Title"
    assert updated_task["description"] == "Updated task description"
    assert updated_task["completed"] is True
    print("✓ Task updated successfully")

    # Step 5: Verify the update by retrieving the task
    get_response = client.get(f"/tasks/{original_task_id}", headers=headers)
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["title"] == "Updated Task Title"
    assert retrieved_task["completed"] is True
    print("✓ Updated task retrieved and verified")

    # Step 6: Delete the task
    delete_response = client.delete(f"/tasks/{original_task_id}", headers=headers)
    assert delete_response.status_code == 200
    print("✓ Task deleted successfully")

    # Step 7: Verify the task no longer exists
    get_deleted_response = client.get(f"/tasks/{original_task_id}", headers=headers)
    assert get_deleted_response.status_code == 404
    print("✓ Deleted task confirmed as removed (404 response)")


def test_signup_task_validation_pipeline(client: TestClient, session: Session):
    """
    Test the signup and task creation pipeline with various validation scenarios.

    Ensures proper validation occurs at each step of the pipeline.
    """
    # Step 1: Signup a new user
    signup_data = {
        "email": "validation_test@example.com",
        "password": "SecureValidPass123!",
        "first_name": "Validation",
        "last_name": "Test"
    }

    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in [200, 201]
    user_data = signup_response.json()
    assert user_data["email"] == "validation_test@example.com"
    print("✓ User signed up successfully")

    # Step 2: Login to get token
    login_response = client.post("/auth/login", json=signup_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ User logged in successfully")

    # Step 3: Create a task with minimal required fields (only title)
    minimal_task_data = {"title": "Minimal Task"}
    minimal_response = client.post("/tasks", json=minimal_task_data, headers=headers)
    assert minimal_response.status_code in [200, 201]
    minimal_task = minimal_response.json()
    assert minimal_task["title"] == "Minimal Task"
    assert minimal_task["description"] is None  # Should default to None
    assert minimal_task["completed"] is False   # Should default to False
    print("✓ Task created with minimal required fields")

    # Step 4: Create a task with all fields including due date
    import datetime
    future_date = (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()

    full_task_data = {
        "title": "Full Featured Task",
        "description": "Task with all available fields populated",
        "completed": False,
        "due_date": future_date
    }

    full_response = client.post("/tasks", json=full_task_data, headers=headers)
    assert full_response.status_code in [200, 201]
    full_task = full_response.json()
    assert full_task["title"] == "Full Featured Task"
    assert full_task["description"] == "Task with all available fields populated"
    assert full_task["completed"] is False
    # Note: The due_date might be reformatted by the API, so we just check it exists
    assert "due_date" in full_task
    print("✓ Task created with all available fields")


if __name__ == "__main__":
    # Allow running this test file directly for development/debugging
    pytest.main([__file__, "-v"])