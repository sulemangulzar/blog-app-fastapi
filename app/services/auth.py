from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import hashed_password
from app.models.user import User
from app.schemas.auth import RegisterUser


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, credentials: RegisterUser):
        existing_user_email = await self.session.execute(
            select(User).where(User.email == credentials.email)
        )

        if existing_user_email:
            raise HTTPException(status_code=400, detail="User With This Email Exists!")

        existing_user_username = await self.session.execute(
            select(User).where(User.username == credentials.username)
        )

        if existing_user_username:
            raise HTTPException(
                status_code=400, detail="User With This Username Exists!"
            )

        new_user = User(
            # 1. Unpack all the safe fields (excluding the raw email and password)
            **credentials.model_dump(exclude={"email", "password"}),
            # 2. Pass the modified fields as direct keyword arguments to User()
            email=str(credentials.email),
            hashed_password=hashed_password(credentials.password),
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
