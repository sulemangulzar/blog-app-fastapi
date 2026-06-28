from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import UserServiceDep, get_current_user
from app.models.user import User
from app.schemas.auth import RegisterUser, UpdateUser, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(service: UserServiceDep, user: RegisterUser):
    return await service.register(user)


@router.post("/login")
async def login(service: UserServiceDep, form: OAuth2PasswordRequestForm = Depends()):
    return await service.login(form.username, form.password)


@router.post("/refresh")
async def refresh(service: UserServiceDep, request: Request):
    return await service.refresh(request)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update(
    user_data: UpdateUser,
    service: UserServiceDep,
    current_user: User = Depends(get_current_user),
):
    return await service.update(current_user.id, user_data)
