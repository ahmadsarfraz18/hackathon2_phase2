from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import timedelta
from ..models.user import User, UserCreate, UserLogin, UserRead
from ..services.auth import authenticate_user
from ..services.user_service import create_user, get_user_by_email
from ..core.database import get_db
from ..core.security import create_access_token
from ..api.deps import get_current_user_from_token
from typing import Dict, Any
import re

router = APIRouter(prefix="/auth", tags=["auth"])


def validate_email_format(email: str) -> bool:
    """
    Validate email format using a basic regex pattern.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength requirements.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check bcrypt limitation: password cannot be longer than 72 bytes
    if len(password.encode('utf-8')) > 72:
        return False, "Password cannot be longer than 72 bytes"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, ""


@router.post("/signup", response_model=UserRead)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    Args:
        user: User creation data including email, password, and optional name fields
        db: Database session dependency

    Returns:
        UserRead: Created user information (excluding password)

    Raises:
        HTTPException: If email is already registered or validation fails
    """
    # Validate email format
    if not validate_email_format(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(user.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Check if user with this email already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )

    # Create new user using the user service
    try:
        db_user = create_user(db, user)
        return db_user
    except Exception as e:
        db.rollback()  # Rollback in case of error
        # Log the actual error in a real application
        print(f"Signup error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.post("/login")
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token.

    Args:
        user_credentials: User login data including email and password
        db: Database session dependency

    Returns:
        Dict: Contains access_token and token_type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Validate email format
    if not validate_email_format(user_credentials.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Authenticate user
    user = authenticate_user(
        session=db,
        email=user_credentials.email,
        password=user_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT access token
    access_token_expires = timedelta(minutes=60)  # Token expires in 1 hour
    access_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
async def refresh_token():
    """
    Refresh the access token (placeholder implementation).

    This endpoint would normally take a refresh token and return a new access token.
    For simplicity in this implementation, we're not implementing refresh tokens.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token functionality not implemented in this version"
    )


@router.get("/me", response_model=UserRead)
async def get_current_user(current_user: User = Depends(get_current_user_from_token)):
    """
    Get current user information based on JWT token.

    Args:
        current_user: User object extracted from JWT token via dependency

    Returns:
        UserRead: Current user information
    """
    return current_user