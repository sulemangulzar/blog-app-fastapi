from datetime import datetime

from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str
    slug: str
    is_published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserInfo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field()
    email: str = Field(index=True, unique=True)
    password_hash: str = Field()
