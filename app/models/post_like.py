from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


class PostLike(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: UUID = Field(foreign_key="post.id", primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="likes")
    post: "Post" = Relationship(back_populates="likes")
