from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.post_tag import PostTagLink

if TYPE_CHECKING:
    from app.models.post import Post


class Tag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, nullable=False, index=True)

    posts: list["Post"] = Relationship(back_populates="tags", link_model=PostTagLink)
