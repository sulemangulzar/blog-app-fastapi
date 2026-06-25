from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.post_tag import PostTagLink

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.tags import Tag
    from app.models.user import User


class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(nullable=False, index=True)
    content: str = Field(nullable=False)
    author_id: UUID = Field(foreign_key="user.id", nullable=False)
    published_status: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    author: "User" = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(back_populates="post")
    tags: list["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)
