from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Text, func
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
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": func.now()},
    )
    deleted_at: datetime | None = Field(default=None)

    post: "Post" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")

    replies: list["Comment"] = Relationship(
        sa_relationship_kwargs=dict(cascade="all, delete-orphan", backref="parent")
    )
