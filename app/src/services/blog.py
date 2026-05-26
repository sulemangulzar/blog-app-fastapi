from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.models.blog import Post, UserInfo
from app.src.schemas.blog import PostCreate, PublishPost


class BlogService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self):
        result = await self.session.execute(select(Post))
        posts = result.scalars().all()
        return posts

    async def get(self, id: UUID):
        post = await self.session.get(Post, id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    async def add(self, post: PostCreate, user: UserInfo):
        add_post = Post(**post.model_dump(), user_id=user.id)
        self.session.add(add_post)
        await self.session.commit()
        await self.session.refresh(add_post)
        return add_post

    async def publish(self, id: UUID, data: PublishPost):
        post = await self.session.get(Post, id)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        post.is_published = data.is_published
        post.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(post)

        return post

    async def update(self, id: UUID, data):
        post = await self.session.get(Post, id)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(post, key, value)
        post.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(post)

        return post

    async def delete(self, id: UUID):
        post = await self.session.get(Post, id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        await self.session.delete(post)
        await self.session.commit()
        return {"message": "Post deleted successfully"}
