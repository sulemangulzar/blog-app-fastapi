from typing import Annotated

from fastapi import APIRouter, Depends

from app.src.api.dependencies import get_access_token, userServiceDep
from app.src.database.redis import add_jti_to_blacklist
from app.src.schemas.user import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", response_model=UserRead, status_code=201)
async def signup(user: UserCreate, service: userServiceDep):
    return await service.create_user(user)


@router.post("/login", response_model=Token)
async def login_user(user: UserLogin, service: userServiceDep):
    return await service.login_user(str(user.email), user.password)


@router.post("/logout")
async def logout(token_data: Annotated[dict, Depends(get_access_token)]):
    await add_jti_to_blacklist(token_data["jti"])

    return {"details": "Successfully Logged Out!"}
