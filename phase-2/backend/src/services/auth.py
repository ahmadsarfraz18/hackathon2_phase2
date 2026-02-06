from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlmodel import Session, select
from ..models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    # Ensure password doesn't exceed bcrypt's 72-byte limit
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the given data and expiration time.

    Args:
        data: Dictionary containing the claims to include in the token
        expires_delta: Optional timedelta for token expiration (defaults to 1 hour)

    Returns:
        Encoded JWT token as string
    """
    import os
    SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-change-me")
    ALGORITHM = "HS256"

    to_encode = data.copy()

    # Set default expiration if not provided
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)  # Default 1 hour

    # Add expiration to the token payload
    to_encode.update({"exp": expire})

    # Encode the token using HS256 algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the decoded payload if valid.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload as dictionary if valid, None if invalid
    """
    import os
    SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-change-me")
    ALGORITHM = "HS256"

    try:
        # Decode the token using the same secret and algorithm
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        print("Token has expired")
        return None
    except (jwt.InvalidTokenError, jwt.DecodeError) as e:
        # Invalid token
        print(f"Invalid token: {e}")
        return None

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.

    Args:
        session: Database session
        email: User's email address
        password: Plain text password

    Returns:
        User object if authentication succeeds, None if it fails
    """
    try:
        # Find user by email
        statement = select(User).where(User.email == email)
        result = session.execute(statement).first()

        # Check if user exists
        if not result:
            return None

        # Extract the user object from the result tuple
        user = result[0]

        # Verify password is correct
        if not user or not verify_password(password, user.password_hash):
            return None

        return user
    except Exception:
        # Log the exception in a real application
        # For now, just return None to indicate authentication failure
        return None

def get_current_user_from_token(session: Session, token: str) -> Optional[User]:
    """
    Get the current user from a JWT token.

    Args:
        session: Database session
        token: JWT token to decode and verify

    Returns:
        User object if token is valid and user exists, None otherwise
    """
    try:
        # Verify the token
        payload = verify_token(token)
        if not payload:
            return None

        # Extract user_id from token payload
        user_id = payload.get("user_id")
        if not user_id:
            return None

        # Convert the user_id string to UUID to match the database field type
        try:
            user_uuid = uuid.UUID(user_id)
        except (ValueError, TypeError):
            # If the user_id is not a valid UUID string, return None
            return None

        # Find user by ID in the database
        statement = select(User).where(User.id == user_uuid)
        result = session.execute(statement).first()

        # Extract the user object from the result tuple
        user = result[0] if result else None

        return user
    except Exception:
        # Log the exception in a real application
        # For now, just return None to indicate failure
        return None