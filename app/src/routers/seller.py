from fastapi import APIRouter

from app.src.api.dependencies import userServiceDep
from app.src.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", response_model=UserRead, status_code=201)
async def signup(user: UserCreate, service: userServiceDep):
    return await service.create_user(user)
