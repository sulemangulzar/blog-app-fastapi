from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from app.models.comment import Comment
from app.models.post import Post, PostStatus
from app.models.post_bookmark import Bookmark
from app.models.post_like import PostLike
from app.models.tag import PostTagLink, Tag
from app.models.user import User, UserRole
from app.schemas.post import CommentCreate, CommentUpdate, PostCreate, PostUpdate


def load_relationship(attribute: Any):
    return selectinload(cast(Any, attribute))


class PostService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_post_or_404(self, post_id: UUID) -> Post:
        result = await self.session.execute(
            select(Post)
            .where(Post.id == post_id)
            .options(
                load_relationship(Post.tags),
                load_relationship(Post.likes),
                load_relationship(Post.bookmarks),
            )
        )
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    def _check_post_owner_or_admin(self, post: Post, user: User) -> None:
        if post.author_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to modify this post",
            )

    async def _make_unique_slug(
        self, title: str, author_id: UUID, post_id: UUID | None = None
    ) -> str:
        base_slug = slugify(title, max_length=70, word_boundary=True) or "post"
        generated_slug = base_slug
        counter = 1

        while True:
            statement = select(Post).where(
                Post.slug == generated_slug, Post.author_id == author_id
            )
            if post_id is not None:
                statement = statement.where(Post.id != post_id)

            result = await self.session.execute(statement)
            existing_post = result.scalar_one_or_none()
            if existing_post is None:
                return generated_slug

            generated_slug = f"{base_slug}-{counter}"
            counter += 1

    async def _get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        clean_names = sorted(
            {name.strip().lower() for name in tag_names if name.strip()}
        )
        tags: list[Tag] = []

        for name in clean_names:
            result = await self.session.execute(select(Tag).where(Tag.name == name))
            tag = result.scalar_one_or_none()
            if tag is None:
                tag = Tag(name=name)
                self.session.add(tag)
            tags.append(tag)

        return tags

    async def _to_post_response(self, post: Post) -> dict:
        likes_count = len(post.likes) if post.likes is not None else 0
        bookmarks_count = len(post.bookmarks) if post.bookmarks is not None else 0

        return {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "content": post.content,
            "excerpt": post.excerpt,
            "status": post.status,
            "published_at": post.published_at,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author_id": post.author_id,
            "tags": post.tags,
            "likes_count": likes_count,
            "bookmarks_count": bookmarks_count,
        }

    async def create(self, author_id: UUID, post_data: PostCreate) -> dict:
        generated_slug = await self._make_unique_slug(post_data.title, author_id)
        published_at = None
        if post_data.status == PostStatus.PUBLISHED:
            published_at = datetime.now(timezone.utc)

        post_tags = await self._get_or_create_tags(post_data.tags)

        new_post = Post(
            title=post_data.title,
            content=post_data.content,
            excerpt=post_data.excerpt,
            status=post_data.status,
            published_at=published_at,
            slug=generated_slug,
            author_id=author_id,
            tags=post_tags,
        )

        self.session.add(new_post)
        await self.session.commit()
        await self.session.refresh(
            new_post, attribute_names=["tags", "likes", "bookmarks"]
        )
        return await self._to_post_response(new_post)

    async def list_posts(
        self,
        skip: int = 0,
        limit: int = 20,
        status_filter: PostStatus | None = PostStatus.PUBLISHED,
        search: str | None = None,
        tag: str | None = None,
    ) -> list[dict]:
        statement = select(Post).options(
            load_relationship(Post.tags),
            load_relationship(Post.likes),
            load_relationship(Post.bookmarks),
        )

        if status_filter is not None:
            statement = statement.where(Post.status == status_filter)

        if search:
            search_text = f"%{search}%"
            statement = statement.where(
                col(Post.title).ilike(search_text)
                | col(Post.content).ilike(search_text)
            )

        if tag:
            statement = (
                statement.join(PostTagLink, col(PostTagLink.post_id) == col(Post.id))
                .join(Tag, col(Tag.id) == col(PostTagLink.tag_id))
                .where(Tag.name == tag.strip().lower())
            )

        statement = (
            statement.order_by(col(Post.created_at).desc()).offset(skip).limit(limit)
        )
        result = await self.session.execute(statement)
        posts = result.scalars().unique().all()
        return [await self._to_post_response(post) for post in posts]

    async def get_by_id(self, post_id: UUID) -> dict:
        post = await self._get_post_or_404(post_id)
        return await self._to_post_response(post)

    async def get_by_slug(self, slug: str) -> dict:
        result = await self.session.execute(
            select(Post)
            .where(Post.slug == slug)
            .options(
                load_relationship(Post.tags),
                load_relationship(Post.likes),
                load_relationship(Post.bookmarks),
            )
        )
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return await self._to_post_response(post)

    async def update(
        self, post_id: UUID, post_data: PostUpdate, current_user: User
    ) -> dict:
        post = await self._get_post_or_404(post_id)
        self._check_post_owner_or_admin(post, current_user)

        update_data = post_data.model_dump(exclude_unset=True)

        if "title" in update_data and update_data["title"] != post.title:
            post.title = update_data["title"]
            post.slug = await self._make_unique_slug(
                post.title, post.author_id, post.id
            )

        if "content" in update_data:
            post.content = update_data["content"]
        if "excerpt" in update_data:
            post.excerpt = update_data["excerpt"]
        if "status" in update_data:
            old_status = post.status
            post.status = update_data["status"]
            if (
                old_status != PostStatus.PUBLISHED
                and post.status == PostStatus.PUBLISHED
            ):
                post.published_at = datetime.now(timezone.utc)
            if post.status != PostStatus.PUBLISHED:
                post.published_at = None
        if "tags" in update_data and update_data["tags"] is not None:
            post.tags = await self._get_or_create_tags(update_data["tags"])

        post.updated_at = datetime.now(timezone.utc)
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post, attribute_names=["tags", "likes", "bookmarks"])
        return await self._to_post_response(post)

    async def delete(self, post_id: UUID, current_user: User) -> dict[str, str]:
        post = await self._get_post_or_404(post_id)
        self._check_post_owner_or_admin(post, current_user)

        await self.session.delete(post)
        await self.session.commit()
        return {"message": "Post deleted successfully"}

    async def create_comment(
        self, post_id: UUID, author_id: UUID, comment_data: CommentCreate
    ) -> Comment:
        await self._get_post_or_404(post_id)

        if comment_data.parent_comment_id is not None:
            parent = await self.session.get(Comment, comment_data.parent_comment_id)
            if parent is None or parent.post_id != post_id:
                raise HTTPException(status_code=400, detail="Invalid parent comment")

        comment = Comment(
            content=comment_data.content,
            post_id=post_id,
            author_id=author_id,
            parent_comment_id=comment_data.parent_comment_id,
        )
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def list_comments(self, post_id: UUID) -> list[Comment]:
        await self._get_post_or_404(post_id)
        result = await self.session.execute(
            select(Comment)
            .where(Comment.post_id == post_id, col(Comment.deleted_at).is_(None))
            .order_by(col(Comment.created_at).asc())
        )
        return list(result.scalars().all())

    async def update_comment(
        self, comment_id: UUID, comment_data: CommentUpdate, current_user: User
    ) -> Comment:
        comment = await self.session.get(Comment, comment_id)
        if comment is None or comment.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Comment not found")
        if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403, detail="You are not allowed to modify this comment"
            )

        comment.content = comment_data.content
        comment.updated_at = datetime.now(timezone.utc)
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def delete_comment(
        self, comment_id: UUID, current_user: User
    ) -> dict[str, str]:
        comment = await self.session.get(Comment, comment_id)
        if comment is None or comment.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Comment not found")
        if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403, detail="You are not allowed to delete this comment"
            )

        comment.deleted_at = datetime.now(timezone.utc)
        self.session.add(comment)
        await self.session.commit()
        return {"message": "Comment deleted successfully"}

    async def like_post(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        await self._get_post_or_404(post_id)
        existing = await self.session.get(PostLike, (user_id, post_id))
        if existing is not None:
            return {"message": "Post already liked"}

        self.session.add(PostLike(user_id=user_id, post_id=post_id))
        await self.session.commit()
        return {"message": "Post liked successfully"}

    async def unlike_post(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        existing = await self.session.get(PostLike, (user_id, post_id))
        if existing is None:
            raise HTTPException(status_code=404, detail="Like not found")

        await self.session.delete(existing)
        await self.session.commit()
        return {"message": "Post unliked successfully"}

    async def bookmark_post(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        await self._get_post_or_404(post_id)
        existing = await self.session.get(Bookmark, (user_id, post_id))
        if existing is not None:
            return {"message": "Post already bookmarked"}

        self.session.add(Bookmark(user_id=user_id, post_id=post_id))
        await self.session.commit()
        return {"message": "Post bookmarked successfully"}

    async def remove_bookmark(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        existing = await self.session.get(Bookmark, (user_id, post_id))
        if existing is None:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        await self.session.delete(existing)
        await self.session.commit()
        return {"message": "Bookmark removed successfully"}

    async def list_tags(self) -> list[Tag]:
        result = await self.session.execute(select(Tag).order_by(col(Tag.name).asc()))
        return list(result.scalars().all())
