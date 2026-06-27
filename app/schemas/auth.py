from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ENUMS
class SelectUserRole(str, Enum):
    ADMIN = "admin"
    AUTHOR = "author"
    READER = "reader"


# REGISTRATION & ONBOARDING
class RegisterUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str | None = None
    biography: str | None = None
    avatar_url: str | None = None


class VerifyEmail(BaseModel):
    token: str


# LOGIN & TOKENS
class LoginUser(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# PASSWORD MANAGEMENT
class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# PROFILE MANAGEMENT


class UpdateUser(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    display_name: str | None = None
    biography: str | None = None
    avatar_url: str | None = None


# ADMIN ACTIONS
class AdminUpdateUserRole(BaseModel):
    role: SelectUserRole


# OUTBOUND RESPONSES
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    display_name: str | None
    biography: str | None
    avatar_url: str | None
    role: SelectUserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
