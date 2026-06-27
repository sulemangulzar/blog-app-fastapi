from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from app.models.comment import Comment
from app.models.post import Post


class UserRole(str, Enum):
    ADMIN = "admin"
    AUTHOR = "author"
    READER = "reader"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str

    display_name: str | None = Field(default=None)
    biography: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None)

    role: UserRole = Field(default=UserRole.READER)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=func.now()),
    )

    posts: list[Post] = Relationship(back_populates="author")
    comments: list[Comment] = Relationship(back_populates="author")
