from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Text, func
from sqlmodel import Field, Relationship, SQLModel

from app.models.tags import PostTagLink, Tag

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.user import User


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False, max_length=255)
    content: str = Field(sa_type=Text, nullable=False)
    excerpt: str | None = Field(default=None, max_length=500)

    author_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    status: PostStatus = Field(default=PostStatus.DRAFT, index=True)

    published_at: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": func.now()},
    )

    # 5. Relationships
    author: "User" = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(back_populates="post")
    tags: list["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)
