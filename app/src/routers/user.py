from typing import Annotated

from fastapi import APIRouter, Depends
from app.src.utils import decode_token

from app.src.api.dependencies import userServiceDep
from app.src.core.security import oauth_scheme
from app.src.schemas.user import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", response_model=UserRead, status_code=201)
async def signup(user: UserCreate, service: userServiceDep):
    return await service.create_user(user)


@router.post("/login", response_model=Token)
async def login_user(user: UserLogin, service: userServiceDep):
    return await service.login_user(str(user.email), user.password)


@router.get("/dashboard")
async def dashboard(token: Annotated[str, Depends(oauth_scheme)]):
    return decode_token(token)
