from uuid import UUID

from fastapi import APIRouter

from app.src.api.dependencies import serviceDep, userDep
from app.src.schemas.blog import PostCreate, PostRead, PostUpdate, PublishPost

router = APIRouter(prefix="/post")


@router.get("/all", response_model=list[PostRead])
async def get_all_posts(service: serviceDep, user: userDep):
    return await service.get_all()


@router.get("/{id}", response_model=PostRead)
async def get_post(id: UUID, service: serviceDep, user: userDep):
    return await service.get(id)


@router.post("/create", response_model=PostRead)
async def create_post(post: PostCreate, service: serviceDep, user: userDep):
    return await service.add(post, user)


@router.put("/publish/{id}", response_model=PostRead)
async def publish_post(id: UUID, data: PublishPost, service: serviceDep):
    return await service.publish(id, data)


@router.put("/update/{id}", response_model=PostRead)
async def update_post(id: UUID, data: PostUpdate, service: serviceDep):
    return await service.update(id, data)


@router.delete("/delete/{id}")
async def delete_post(id: UUID, service: serviceDep):
    return await service.delete(id)
