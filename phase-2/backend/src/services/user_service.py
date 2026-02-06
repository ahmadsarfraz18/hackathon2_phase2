from sqlmodel import Session, select
from typing import Optional
from ..models.user import User, UserCreate, UserUpdate
from .auth import get_password_hash


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Retrieve a user by their ID.

    Args:
        db: Database session
        user_id: User's unique identifier

    Returns:
        User object if found, None otherwise
    """
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user by their email address.

    Args:
        db: Database session
        email: User's email address

    Returns:
        User object if found, None otherwise
    """
    try:
        statement = select(User).where(User.email == email)
        result = db.execute(statement).first()
        return result[0] if result else None  # Extract user from tuple if exists
    except Exception:
        # Log the exception in a real application
        return None


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db: Database session
        user: User creation data including email, password, and optional name fields

    Returns:
        Created User object
    """
    # Hash the password before storing
    hashed_password = get_password_hash(user.password)

    # Create user instance with hashed password
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )

    # Add to database and commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
    """
    Update user information.

    Args:
        db: Database session
        user_id: ID of the user to update
        user_update: Updated user data

    Returns:
        Updated User object if found, None otherwise
    """
    # Get the existing user
    db_user = db.get(User, user_id)
    if not db_user:
        return None

    # Update user fields if they are provided in the update
    user_data = user_update.dict(exclude_unset=True)
    for field, value in user_data.items():
        setattr(db_user, field, value)

    # Commit changes and refresh
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    """
    Delete a user from the database.

    Args:
        db: Database session
        user_id: ID of the user to delete

    Returns:
        True if user was deleted, False if user was not found
    """
    db_user = db.get(User, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()

    return True


def deactivate_user(db: Session, user_id: str) -> Optional[User]:
    """
    Deactivate a user account (soft delete).

    Args:
        db: Database session
        user_id: ID of the user to deactivate

    Returns:
        Updated User object if found, None otherwise
    """
    db_user = db.get(User, user_id)
    if not db_user:
        return None

    db_user.is_active = False
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def activate_user(db: Session, user_id: str) -> Optional[User]:
    """
    Activate a user account.

    Args:
        db: Database session
        user_id: ID of the user to activate

    Returns:
        Updated User object if found, None otherwise
    """
    db_user = db.get(User, user_id)
    if not db_user:
        return None

    db_user.is_active = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def verify_email(db: Session, user_id: str) -> Optional[User]:
    """
    Mark user's email as verified.

    Args:
        db: Database session
        user_id: ID of the user whose email to verify

    Returns:
        Updated User object if found, None otherwise
    """
    db_user = db.get(User, user_id)
    if not db_user:
        return None

    db_user.email_verified = True
    db_user.email_verification_token = None  # Clear verification token
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user