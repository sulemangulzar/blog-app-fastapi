from datetime import datetime, timezone
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


class PostService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post_model(self, post_id: UUID) -> Post:
        result = await self.session.execute(
            select(Post)
            .where(Post.id == post_id)
            .options(
                selectinload(Post.tags),  # type: ignore[arg-type]
                selectinload(Post.likes),  # type: ignore[arg-type]
                selectinload(Post.bookmarks),  # type: ignore[arg-type]
            )
        )
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        return post

    def check_post_permission(self, post: Post, user: User) -> None:
        is_author = post.author_id == user.id
        is_admin = user.role == UserRole.ADMIN

        if not is_author and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to modify this post",
            )

    async def create_unique_slug(
        self, title: str, author_id: UUID, current_post_id: UUID | None = None
    ) -> str:
        base_slug = slugify(title, max_length=70, word_boundary=True) or "post"
        slug = base_slug
        counter = 1

        while True:
            statement = select(Post).where(
                Post.slug == slug, Post.author_id == author_id
            )

            if current_post_id is not None:
                statement = statement.where(Post.id != current_post_id)

            result = await self.session.execute(statement)
            existing_post = result.scalar_one_or_none()

            if existing_post is None:
                return slug

            slug = f"{base_slug}-{counter}"
            counter += 1

    async def get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        tags: list[Tag] = []
        clean_names = set()

        for name in tag_names:
            clean_name = name.strip().lower()
            if clean_name:
                clean_names.add(clean_name)

        for name in sorted(clean_names):
            result = await self.session.execute(select(Tag).where(Tag.name == name))
            tag = result.scalar_one_or_none()

            if tag is None:
                tag = Tag(name=name)
                self.session.add(tag)

            tags.append(tag)

        return tags

    def post_to_response(self, post: Post) -> dict:
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
            "likes_count": len(post.likes),
            "bookmarks_count": len(post.bookmarks),
        }

    async def create(self, author_id: UUID, post_data: PostCreate) -> dict:
        slug = await self.create_unique_slug(post_data.title, author_id)
        tags = await self.get_or_create_tags(post_data.tags)

        published_at = None
        if post_data.status == PostStatus.PUBLISHED:
            published_at = datetime.now(timezone.utc)

        post = Post(
            title=post_data.title,
            slug=slug,
            content=post_data.content,
            excerpt=post_data.excerpt,
            status=post_data.status,
            published_at=published_at,
            author_id=author_id,
            tags=tags,
        )

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post, attribute_names=["tags", "likes", "bookmarks"])

        return self.post_to_response(post)

    async def list_posts(
        self,
        skip: int = 0,
        limit: int = 20,
        status_filter: PostStatus | None = PostStatus.PUBLISHED,
        search: str | None = None,
        tag: str | None = None,
    ) -> list[dict]:
        statement = select(Post).options(
            selectinload(Post.tags),  # type: ignore[arg-type]
            selectinload(Post.likes),  # type: ignore[arg-type]
            selectinload(Post.bookmarks),  # type: ignore[arg-type]
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
            clean_tag = tag.strip().lower()
            statement = (
                statement.join(PostTagLink, col(PostTagLink.post_id) == col(Post.id))
                .join(Tag, col(Tag.id) == col(PostTagLink.tag_id))
                .where(Tag.name == clean_tag)
            )

        statement = (
            statement.order_by(col(Post.created_at).desc()).offset(skip).limit(limit)
        )
        result = await self.session.execute(statement)
        posts = result.scalars().unique().all()

        return [self.post_to_response(post) for post in posts]

    async def get_by_id(self, post_id: UUID) -> dict:
        post = await self.get_post_model(post_id)
        return self.post_to_response(post)

    async def get_by_slug(self, slug: str) -> dict:
        result = await self.session.execute(
            select(Post)
            .where(Post.slug == slug)
            .options(
                selectinload(Post.tags),  # type: ignore[arg-type]
                selectinload(Post.likes),  # type: ignore[arg-type]
                selectinload(Post.bookmarks),  # type: ignore[arg-type]
            )
        )
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        return self.post_to_response(post)

    async def update(
        self, post_id: UUID, post_data: PostUpdate, current_user: User
    ) -> dict:
        post = await self.get_post_model(post_id)
        self.check_post_permission(post, current_user)

        if post_data.title is not None:
            post.title = post_data.title
            post.slug = await self.create_unique_slug(
                post.title, post.author_id, post.id
            )

        if post_data.content is not None:
            post.content = post_data.content

        if post_data.excerpt is not None:
            post.excerpt = post_data.excerpt

        if post_data.status is not None:
            post.status = post_data.status

            if post.status == PostStatus.PUBLISHED and post.published_at is None:
                post.published_at = datetime.now(timezone.utc)

            if post.status != PostStatus.PUBLISHED:
                post.published_at = None

        if post_data.tags is not None:
            post.tags = await self.get_or_create_tags(post_data.tags)

        post.updated_at = datetime.now(timezone.utc)

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post, attribute_names=["tags", "likes", "bookmarks"])

        return self.post_to_response(post)

    async def delete(self, post_id: UUID, current_user: User) -> dict[str, str]:
        post = await self.get_post_model(post_id)
        self.check_post_permission(post, current_user)

        await self.session.delete(post)
        await self.session.commit()

        return {"message": "Post deleted successfully"}

    async def create_comment(
        self, post_id: UUID, author_id: UUID, comment_data: CommentCreate
    ) -> Comment:
        await self.get_post_model(post_id)

        if comment_data.parent_comment_id is not None:
            parent_comment = await self.session.get(
                Comment, comment_data.parent_comment_id
            )

            if parent_comment is None or parent_comment.post_id != post_id:
                raise HTTPException(status_code=400, detail="Invalid parent comment")

        comment = Comment(
            content=comment_data.content,
            author_id=author_id,
            post_id=post_id,
            parent_comment_id=comment_data.parent_comment_id,
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)

        return comment

    async def list_comments(self, post_id: UUID) -> list[Comment]:
        await self.get_post_model(post_id)

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

        is_author = comment.author_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not is_author and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to modify this comment",
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

        is_author = comment.author_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not is_author and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to delete this comment",
            )

        comment.deleted_at = datetime.now(timezone.utc)

        self.session.add(comment)
        await self.session.commit()

        return {"message": "Comment deleted successfully"}

    async def like_post(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        await self.get_post_model(post_id)

        existing_like = await self.session.get(PostLike, (user_id, post_id))
        if existing_like is not None:
            return {"message": "Post already liked"}

        like = PostLike(user_id=user_id, post_id=post_id)
        self.session.add(like)
        await self.session.commit()

        return {"message": "Post liked successfully"}

    async def unlike_post(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        existing_like = await self.session.get(PostLike, (user_id, post_id))

        if existing_like is None:
            raise HTTPException(status_code=404, detail="Like not found")

        await self.session.delete(existing_like)
        await self.session.commit()

        return {"message": "Post unliked successfully"}

    async def bookmark_post(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        await self.get_post_model(post_id)

        existing_bookmark = await self.session.get(Bookmark, (user_id, post_id))
        if existing_bookmark is not None:
            return {"message": "Post already bookmarked"}

        bookmark = Bookmark(user_id=user_id, post_id=post_id)
        self.session.add(bookmark)
        await self.session.commit()

        return {"message": "Post bookmarked successfully"}

    async def remove_bookmark(self, post_id: UUID, user_id: UUID) -> dict[str, str]:
        existing_bookmark = await self.session.get(Bookmark, (user_id, post_id))

        if existing_bookmark is None:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        await self.session.delete(existing_bookmark)
        await self.session.commit()

        return {"message": "Bookmark removed successfully"}

    async def list_tags(self) -> list[Tag]:
        result = await self.session.execute(select(Tag).order_by(col(Tag.name).asc()))
        return list(result.scalars().all())
