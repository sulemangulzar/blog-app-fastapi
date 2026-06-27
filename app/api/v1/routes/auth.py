from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.auth import RegisterUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(session: SessionDep, user: RegisterUser):
    pass
