from datetime import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    slug: str
    is_published: bool


class PostRead(BaseModel):
    id: int
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
