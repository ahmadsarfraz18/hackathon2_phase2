from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class UserBase(SQLModel):
    """Base model for user with common fields"""
    email: str = Field(unique=True, index=True)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """User model for database table"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str = Field(sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    email_verified: bool = Field(default=False)
    email_verification_token: Optional[str] = Field(default=None)


class UserRead(UserBase):
    """Schema for reading user data"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    email_verified: bool


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    # Email verification will be handled separately if needed


class UserUpdate(SQLModel):
    """Schema for updating user data"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UserLogin(SQLModel):
    """Schema for user login"""
    email: str
    password: str


class UserPublic(UserBase):
    """Public-facing user schema without sensitive data"""
    id: uuid.UUID
    created_at: datetime
    email_verified: bool