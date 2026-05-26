from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.src.models.blog import UserInfo
from app.src.schemas.user import UserCreate
from app.src.utils import create_access_token

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, credentials: UserCreate):
        existing_user = await self.session.execute(
            select(UserInfo).where(col(UserInfo.email) == str(credentials.email))
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already registered")

        user = UserInfo(
            **credentials.model_dump(exclude={"email", "password"}),
            email=str(credentials.email),
            password_hash=password_context.hash(credentials.password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def login_user(self, email: str, password: str):
        result = await self.session.execute(
            select(UserInfo).where(col(UserInfo.email) == email)
        )

        user = result.scalar_one_or_none()

        if user is None or not password_context.verify(password, user.password_hash):
            raise HTTPException(
                status_code=401, detail="Email or password is incorrect"
            )
        token = create_access_token(
            data={"user": {"name": user.name, "id": str(user.id)}}
        )

        return {"access_token": token, "token_type": "bearer"}
