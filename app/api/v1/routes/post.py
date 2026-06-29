from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import PostServiceDep, get_current_user
from app.models.post import PostStatus
from app.models.user import User
from app.schemas.post import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    MessageResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
    TagResponse,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.create(current_user.id, post)


@router.get("/", response_model=list[PostResponse])
async def list_posts(
    service: PostServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: PostStatus | None = Query(default=PostStatus.PUBLISHED),
    search: str | None = None,
    tag: str | None = None,
):
    return await service.list_posts(skip, limit, status_filter, search, tag)


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(service: PostServiceDep):
    return await service.list_tags()


@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(slug: str, service: PostServiceDep):
    return await service.get_by_slug(slug)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, service: PostServiceDep):
    return await service.get_by_id(post_id)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post: PostUpdate,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.update(post_id, post, current_user)


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(
    post_id: UUID,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.delete(post_id, current_user)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: UUID,
    comment: CommentCreate,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.create_comment(post_id, current_user.id, comment)


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(post_id: UUID, service: PostServiceDep):
    return await service.list_comments(post_id)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    comment: CommentUpdate,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.update_comment(comment_id, comment, current_user)


@router.delete("/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: UUID,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.delete_comment(comment_id, current_user)


@router.post("/{post_id}/like", response_model=MessageResponse)
async def like_post(
    post_id: UUID,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.like_post(post_id, current_user.id)


@router.delete("/{post_id}/like", response_model=MessageResponse)
async def unlike_post(
    post_id: UUID,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.unlike_post(post_id, current_user.id)


@router.post("/{post_id}/bookmark", response_model=MessageResponse)
async def bookmark_post(
    post_id: UUID,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.bookmark_post(post_id, current_user.id)


@router.delete("/{post_id}/bookmark", response_model=MessageResponse)
async def remove_bookmark(
    post_id: UUID,
    service: PostServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.remove_bookmark(post_id, current_user.id)
