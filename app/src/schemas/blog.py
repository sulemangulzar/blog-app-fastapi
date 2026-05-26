from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.src.models.blog import UserInfo


class PostCreate(BaseModel):
    title: str
    content: str
    slug: str
    is_published: bool


class PostRead(BaseModel):
    id: UUID
    user: UserInfo
    title: str
    content: str
    slug: str
    is_published: bool
    created_at: datetime
    updated_at: datetime


class PostUpdate(BaseModel):
    title: str
    content: str
    slug: str


class PublishPost(BaseModel):
    is_published: bool = True
