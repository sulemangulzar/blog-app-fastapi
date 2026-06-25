from uuid import UUID

from sqlmodel import Field, SQLModel


class PostTagLink(SQLModel, table=True):
    post_id: UUID = Field(foreign_key="post.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)
