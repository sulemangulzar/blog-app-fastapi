from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.post import PostStatus


class TagResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    content: str = Field(..., min_length=1)
    excerpt: str | None = Field(default=None, max_length=500)
    status: PostStatus = Field(default=PostStatus.DRAFT)
    tags: list[str] = Field(default_factory=list)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    content: str | None = Field(default=None, min_length=1)
    excerpt: str | None = Field(default=None, max_length=500)
    status: PostStatus | None = None
    tags: list[str] | None = None


class PostResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    content: str
    excerpt: str | None
    status: PostStatus
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author_id: UUID
    tags: list[TagResponse] = Field(default_factory=list)
    likes_count: int = 0
    bookmarks_count: int = 0


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    parent_comment_id: UUID | None = None


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: UUID
    content: str
    author_id: UUID
    post_id: UUID
    parent_comment_id: UUID | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
