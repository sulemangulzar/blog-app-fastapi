from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, SQLModel
from sqlmodel.main import Relationship


class Post(SQLModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    title: str
    content: str
    slug: str
    user_id: UUID = Field(foreign_key="userinfo.id")
    user: "UserInfo" = Relationship(
        back_populates="blogs", sa_relationship_kwargs={"lazy": "selectin"}
    )
    is_published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserInfo(SQLModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    name: str = Field()
    email: str = Field(index=True, unique=True)
    password_hash: str = Field()
    blogs: list[Post] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
