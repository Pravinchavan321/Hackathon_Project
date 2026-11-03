"""User models and schemas."""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class UserRole(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserBase(BaseModel):
    email: str = Field(..., min_length=3, description="User email address")
    full_name: str
    department: Optional[str] = "General"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    role: Optional[UserRole] = UserRole.EMPLOYEE


class UserLogin(BaseModel):
    email: str = Field(..., min_length=3)
    password: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    role: UserRole
    status: UserStatus
    created_at: datetime


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    password_hash: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
