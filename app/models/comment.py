from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, Relationship, SQLModel

# Protect against circular imports
if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


class Comment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str = Field(sa_type=Text, nullable=False)

    author_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    post_id: UUID = Field(foreign_key="post.id", index=True, nullable=False)

    parent_comment_id: UUID | None = Field(
        default=None, foreign_key="comment.id", index=True
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            "created_at",
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=func.now()),
    )
    deleted_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    post: "Post" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")

    parent: Optional["Comment"] = Relationship(
        back_populates="replies", sa_relationship_kwargs={"remote_side": "Comment.id"}
    )

    # 2. Update replies to use back_populates instead of backref
    replies: list["Comment"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
