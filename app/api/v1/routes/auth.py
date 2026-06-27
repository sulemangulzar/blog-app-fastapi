from fastapi import APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import UserServiceDep
from app.schemas.auth import RegisterUser, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(service: UserServiceDep, user: RegisterUser):
    return await service.register(user)


@router.post(
    "/login",
)
async def login(service: UserServiceDep, form: OAuth2PasswordRequestForm):
    return await service.login(form.username, form.password)
