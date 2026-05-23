from fastapi import APIRouter

from ..routers import posts, seller

master_router = APIRouter()

master_router.include_router(posts.router)
master_router.include_router(seller.router)
