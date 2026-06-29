from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, Relationship, SQLModel

from app.models.post_bookmark import Bookmark
from app.models.post_like import PostLike
from app.models.tag import PostTagLink

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.tag import Tag
    from app.models.user import User


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(index=True, nullable=False)
    content: str = Field(sa_type=Text, nullable=False)
    excerpt: str | None = Field(default=None, max_length=500)

    author_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    status: PostStatus = Field(default=PostStatus.DRAFT, index=True)

    published_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=func.now()),
    )

    # 5. Relationships
    author: "User" = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(back_populates="post")
    tags: list["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)
    likes: list["PostLike"] = Relationship(back_populates="post")
    bookmarks: list["Bookmark"] = Relationship(back_populates="post")
