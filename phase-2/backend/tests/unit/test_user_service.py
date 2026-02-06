import pytest
from unittest.mock import MagicMock
from sqlmodel import Session
from backend.src.models.user import User, UserCreate, UserUpdate
from backend.src.services.user_service import (
    get_user_by_id,
    get_user_by_email,
    create_user,
    update_user,
    delete_user,
    deactivate_user,
    activate_user,
    verify_email
)
from backend.src.services.auth import get_password_hash


def test_get_user_by_id_found():
    """Test retrieving a user by ID when user exists."""
    # Mock session and user
    mock_session = MagicMock(spec=Session)
    expected_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("password"),
        first_name="Test",
        last_name="User"
    )

    # Mock the get method to return the user
    mock_session.get.return_value = expected_user

    # Test the function
    result = get_user_by_id(mock_session, "test-user-id")

    # Verify the result
    assert result == expected_user
    mock_session.get.assert_called_once_with(User, "test-user-id")


def test_get_user_by_id_not_found():
    """Test retrieving a user by ID when user does not exist."""
    # Mock session to return None
    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = None

    # Test the function
    result = get_user_by_id(mock_session, "nonexistent-id")

    # Verify the result
    assert result is None


def test_get_user_by_email_found():
    """Test retrieving a user by email when user exists."""
    # Mock session and user
    mock_session = MagicMock(spec=Session)
    expected_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("password"),
        first_name="Test",
        last_name="User"
    )

    # Mock the exec method to return the user
    mock_result = MagicMock()
    mock_result.first.return_value = expected_user
    mock_session.exec.return_value = mock_result

    # Test the function
    result = get_user_by_email(mock_session, "test@example.com")

    # Verify the result
    assert result == expected_user


def test_get_user_by_email_not_found():
    """Test retrieving a user by email when user does not exist."""
    # Mock session to return None
    mock_session = MagicMock(spec=Session)
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    # Test the function
    result = get_user_by_email(mock_session, "nonexistent@example.com")

    # Verify the result
    assert result is None


def test_create_user_success():
    """Test creating a new user successfully."""
    # Mock session
    mock_session = MagicMock(spec=Session)

    # Create user data
    user_create = UserCreate(
        email="newuser@example.com",
        password="securepassword123",
        first_name="New",
        last_name="User"
    )

    # Call the function
    result = create_user(mock_session, user_create)

    # Verify the result
    assert result.email == "newuser@example.com"
    assert result.first_name == "New"
    assert result.last_name == "User"
    # Password should be hashed, not plain text
    assert result.password_hash != "securepassword123"

    # Verify session methods were called
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_update_user_success():
    """Test updating a user successfully."""
    # Mock session and existing user
    mock_session = MagicMock(spec=Session)
    existing_user = User(
        id="test-user-id",
        email="old@example.com",
        password_hash=get_password_hash("oldpassword"),
        first_name="Old",
        last_name="User"
    )
    mock_session.get.return_value = existing_user

    # Create update data
    user_update = UserUpdate(
        email="new@example.com",
        first_name="Updated"
    )

    # Call the function
    result = update_user(mock_session, "test-user-id", user_update)

    # Verify the result
    assert result is not None
    assert result.email == "new@example.com"
    assert result.first_name == "Updated"
    assert result.last_name == "User"  # Unchanged field should remain the same


def test_update_user_not_found():
    """Test updating a user that doesn't exist."""
    # Mock session to return None
    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = None

    # Create update data
    user_update = UserUpdate(first_name="Updated")

    # Call the function
    result = update_user(mock_session, "nonexistent-id", user_update)

    # Verify the result
    assert result is None


def test_delete_user_success():
    """Test deleting a user successfully."""
    # Mock session and existing user
    mock_session = MagicMock(spec=Session)
    existing_user = User(
        id="test-user-id",
        email="todelete@example.com",
        password_hash=get_password_hash("password"),
        first_name="To",
        last_name="Delete"
    )
    mock_session.get.return_value = existing_user

    # Call the function
    result = delete_user(mock_session, "test-user-id")

    # Verify the result
    assert result is True
    mock_session.delete.assert_called_once_with(existing_user)
    mock_session.commit.assert_called_once()


def test_delete_user_not_found():
    """Test deleting a user that doesn't exist."""
    # Mock session to return None
    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = None

    # Call the function
    result = delete_user(mock_session, "nonexistent-id")

    # Verify the result
    assert result is False


def test_deactivate_user_success():
    """Test deactivating a user successfully."""
    # Mock session and existing user
    mock_session = MagicMock(spec=Session)
    existing_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        is_active=True
    )
    mock_session.get.return_value = existing_user

    # Call the function
    result = deactivate_user(mock_session, "test-user-id")

    # Verify the result
    assert result is not None
    assert result.is_active is False


def test_deactivate_user_not_found():
    """Test deactivating a user that doesn't exist."""
    # Mock session to return None
    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = None

    # Call the function
    result = deactivate_user(mock_session, "nonexistent-id")

    # Verify the result
    assert result is None


def test_activate_user_success():
    """Test activating a user successfully."""
    # Mock session and existing user
    mock_session = MagicMock(spec=Session)
    existing_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        is_active=False
    )
    mock_session.get.return_value = existing_user

    # Call the function
    result = activate_user(mock_session, "test-user-id")

    # Verify the result
    assert result is not None
    assert result.is_active is True


def test_activate_user_not_found():
    """Test activating a user that doesn't exist."""
    # Mock session to return None
    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = None

    # Call the function
    result = activate_user(mock_session, "nonexistent-id")

    # Verify the result
    assert result is None


def test_verify_email_success():
    """Test verifying a user's email successfully."""
    # Mock session and existing user
    mock_session = MagicMock(spec=Session)
    existing_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        email_verified=False,
        email_verification_token="some-token"
    )
    mock_session.get.return_value = existing_user

    # Call the function
    result = verify_email(mock_session, "test-user-id")

    # Verify the result
    assert result is not None
    assert result.email_verified is True
    assert result.email_verification_token is None  # Token should be cleared


def test_verify_email_not_found():
    """Test verifying email for a user that doesn't exist."""
    # Mock session to return None
    mock_session = MagicMock(spec=Session)
    mock_session.get.return_value = None

    # Call the function
    result = verify_email(mock_session, "nonexistent-id")

    # Verify the result
    assert result is None


def test_create_user_password_hashing():
    """Test that user passwords are properly hashed during creation."""
    # Mock session
    mock_session = MagicMock(spec=Session)

    # Create user data
    user_create = UserCreate(
        email="hash.test@example.com",
        password="plainpassword",
        first_name="Hash",
        last_name="Test"
    )

    # Call the function
    result = create_user(mock_session, user_create)

    # Verify that the stored password is hashed, not plain text
    assert result.password_hash != "plainpassword"
    # Verify that the hash is valid by checking if it can be verified
    from backend.src.services.auth import verify_password
    assert verify_password("plainpassword", result.password_hash) is True


def test_update_user_partial_update():
    """Test updating only some user fields."""
    # Mock session and existing user
    mock_session = MagicMock(spec=Session)
    existing_user = User(
        id="test-user-id",
        email="old@example.com",
        password_hash=get_password_hash("password"),
        first_name="Old",
        last_name="User"
    )
    mock_session.get.return_value = existing_user

    # Create partial update data (only update first_name)
    user_update = UserUpdate(first_name="Updated")

    # Call the function
    result = update_user(mock_session, "test-user-id", user_update)

    # Verify only the specified field was updated
    assert result.first_name == "Updated"
    assert result.email == "old@example.com"  # Unchanged
    assert result.last_name == "User"  # Unchanged