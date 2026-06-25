from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


class Comment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str = Field(nullable=False)
    author_id: UUID = Field(foreign_key="user.id", nullable=False)
    post_id: UUID = Field(foreign_key="post.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    author: "User" = Relationship(back_populates="comments")
    post: "Post" = Relationship(back_populates="comments")
