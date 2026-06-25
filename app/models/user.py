from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.post import Post


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, nullable=False, index=True)
    email: EmailStr = Field(unique=True, nullable=False, index=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    posts: list["Post"] = Relationship(back_populates="author")
    comments: list["Comment"] = Relationship(back_populates="author")
