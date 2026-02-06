import pytest
from unittest.mock import patch, MagicMock
from sqlmodel import Session
from backend.src.models.user import User
from backend.src.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    authenticate_user
)
from datetime import timedelta, datetime
import os


def test_password_hashing():
    """Test that password hashing and verification work correctly."""
    password = "securepassword123"
    wrong_password = "wrongpassword"

    # Test hashing
    hashed = get_password_hash(password)
    assert hashed != password  # Hash should not be the same as plain text

    # Test verification with correct password
    assert verify_password(password, hashed) == True

    # Test verification with wrong password
    assert verify_password(wrong_password, hashed) == False


def test_create_access_token():
    """Test that access tokens are created correctly."""
    # Mock environment variable for testing
    os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"

    data = {"user_id": "test-user-id", "email": "test@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))

    assert isinstance(token, str)
    assert len(token) > 0
    assert token.startswith("eyJ")  # JWT tokens start with "eyJ" when base64 encoded


def test_verify_token_valid():
    """Test that valid tokens can be verified."""
    os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"

    data = {"user_id": "test-user-id", "email": "test@example.com"}
    token = create_access_token(data, expires_delta=timedelta(hours=1))

    payload = verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "test-user-id"
    assert payload["email"] == "test@example.com"


def test_verify_token_invalid():
    """Test that invalid tokens return None."""
    # Test with completely invalid token
    payload = verify_token("invalid.token.here")
    assert payload is None


def test_verify_token_expired():
    """Test that expired tokens return None."""
    os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"

    data = {"user_id": "test-user-id", "email": "test@example.com"}
    # Create a token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=1))

    # Sleep to ensure token expires
    import time
    time.sleep(2)

    payload = verify_token(token)
    assert payload is None


def test_authenticate_user_success():
    """Test successful user authentication."""
    # Mock session and user
    mock_session = MagicMock(spec=Session)
    mock_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("correctpassword"),
        first_name="Test",
        last_name="User"
    )

    # Mock the exec method to return the user
    mock_result = MagicMock()
    mock_result.first.return_value = mock_user
    mock_session.exec.return_value = mock_result

    # Test authentication with correct credentials
    authenticated_user = authenticate_user(mock_session, "test@example.com", "correctpassword")
    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"


def test_authenticate_user_wrong_password():
    """Test authentication failure with wrong password."""
    # Mock session and user
    mock_session = MagicMock(spec=Session)
    mock_user = User(
        id="test-user-id",
        email="test@example.com",
        password_hash=get_password_hash("correctpassword"),
        first_name="Test",
        last_name="User"
    )

    # Mock the exec method to return the user
    mock_result = MagicMock()
    mock_result.first.return_value = mock_user
    mock_session.exec.return_value = mock_result

    # Test authentication with wrong password
    authenticated_user = authenticate_user(mock_session, "test@example.com", "wrongpassword")
    assert authenticated_user is None


def test_authenticate_user_nonexistent_user():
    """Test authentication failure with non-existent user."""
    # Mock session to return None (no user found)
    mock_session = MagicMock(spec=Session)
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    # Test authentication with non-existent user
    authenticated_user = authenticate_user(mock_session, "nonexistent@example.com", "anypassword")
    assert authenticated_user is None


def test_password_verification_edge_cases():
    """Test password verification with edge cases."""
    # Test with empty password
    hashed = get_password_hash("")
    assert verify_password("", hashed) == True
    assert verify_password("notempty", hashed) == False

    # Test with special characters
    special_password = "p@ssw0rd!$%特殊字符"
    hashed = get_password_hash(special_password)
    assert verify_password(special_password, hashed) == True
    assert verify_password("different", hashed) == False


def test_token_creation_without_expiration():
    """Test token creation with default expiration."""
    os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"

    data = {"user_id": "test-user-id", "email": "test@example.com"}
    token = create_access_token(data)  # No expiration specified, should use default

    assert isinstance(token, str)
    assert len(token) > 0


def test_token_payload_integrity():
    """Test that token payloads maintain integrity."""
    os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"

    original_data = {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "custom_field": "custom_value"
    }
    token = create_access_token(original_data, expires_delta=timedelta(hours=1))

    payload = verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "test-user-id"
    assert payload["email"] == "test@example.com"
    assert payload["custom_field"] == "custom_value"
    assert "exp" in payload  # Expiration should be added automatically