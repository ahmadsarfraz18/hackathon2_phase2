from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from jose import JWTError, jwt
from typing import Optional
import os
import uuid
from datetime import datetime
from ..core.database import get_db
from ..models.user import User
from ..services.auth import verify_token

# Initialize the HTTP Bearer scheme for authentication
security = HTTPBearer(auto_error=True)

# Secret key for JWT signing - should match BETTER_AUTH_SECRET
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-change-me")
if not SECRET_KEY or SECRET_KEY == "fallback-secret-change-me":
    print("WARNING: Using fallback secret key. Please set BETTER_AUTH_SECRET environment variable.")
    SECRET_KEY = "fallback-secret-change-me"

# Algorithm used for JWT encoding/decoding
ALGORITHM = "HS256"


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current user from the JWT token in the request.

    Args:
        credentials: HTTP authorization credentials containing the token
        db: Database session

    Returns:
        User object if token is valid and user exists

    Raises:
        HTTPException: If token is invalid, expired, or user doesn't exist
    """
    token = credentials.credentials

    # Verify the token and extract payload
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token payload
    user_id_str: str = payload.get("user_id")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no user_id in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert the user_id string to UUID to match the database field type
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        # If the user_id is not a valid UUID string, raise an exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - invalid user_id format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Find user by ID in the database
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency to get only the current user ID from the JWT token.

    Args:
        credentials: HTTP authorization credentials containing the token

    Returns:
        User ID string if token is valid

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    # Verify the token and extract payload
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token payload
    user_id: str = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no user_id in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get the current user from the JWT token if present.
    Does not require authentication - returns None if no token or invalid token.

    Args:
        credentials: HTTP authorization credentials containing the token (optional)
        db: Database session

    Returns:
        User object if token is valid and user exists, None otherwise
    """
    try:
        # Try to get credentials
        if not credentials:
            # No authorization header provided
            return None

        token = credentials.credentials

        # Verify the token and extract payload
        payload = verify_token(token)
        if not payload:
            # Token is invalid or expired
            return None

        # Extract user_id from token payload
        user_id: str = payload.get("user_id")
        if not user_id:
            # No user_id in token
            return None

        # Find user by ID in the database
        user = db.get(User, user_id)
        if not user or not user.is_active:
            # User not found or inactive
            return None

        return user
    except Exception:
        # Any error in authentication returns None
        return None