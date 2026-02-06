from datetime import datetime, timedelta
from typing import Optional
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends
from sqlmodel import Session
from jose import JWTError, jwt
from sqlalchemy.orm import Session as DBSession

# Initialize the HTTP Bearer scheme for authentication
security = HTTPBearer()

# Secret key for JWT signing - should match BETTER_AUTH_SECRET
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-change-me")  # Provide a fallback for development
if not SECRET_KEY or SECRET_KEY == "fallback-secret-change-me":
    print("WARNING: Using fallback secret key. Please set BETTER_AUTH_SECRET environment variable.")
    SECRET_KEY = "fallback-secret-change-me"

# Algorithm used for JWT encoding/decoding
ALGORITHM = "HS256"

# Default token expiration time (can be overridden)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the given data and expiration time.

    Args:
        data: Dictionary containing the claims to include in the token
        expires_delta: Optional timedelta for token expiration (defaults to 1 hour)

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Encode the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token_payload(credentials: HTTPAuthorizationCredentials) -> dict:
    """
    Verify the JWT token from the authorization credentials.

    Args:
        credentials: HTTP authorization credentials containing the token

    Returns:
        Decoded token payload if valid

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    token = credentials.credentials

    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract the current user ID from the JWT token in the request.

    Args:
        credentials: HTTP authorization credentials containing the token

    Returns:
        User ID string if token is valid

    Raises:
        HTTPException: If token is invalid, expired, or user_id is missing
    """
    payload = verify_token_payload(credentials)
    user_id: str = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no user_id in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract the current user email from the JWT token in the request.

    Args:
        credentials: HTTP authorization credentials containing the token

    Returns:
        User email string if token is valid

    Raises:
        HTTPException: If token is invalid, expired, or email is missing
    """
    payload = verify_token_payload(credentials)
    email: str = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no email in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return email


def verify_secret_key_configured():
    """
    Verify that the secret key is properly configured.

    Raises:
        ValueError: If SECRET_KEY is not set or is using the default fallback
    """
    if not SECRET_KEY or SECRET_KEY == "":
        raise ValueError("BETTER_AUTH_SECRET environment variable is not set")