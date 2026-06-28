from uuid import UUID

import jwt
from fastapi import HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import get_hashed_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterUser, UpdateUser


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, credentials: RegisterUser) -> User:
        result_email = await self.session.execute(
            select(User).where(User.email == credentials.email)
        )
        if result_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User With This Email Exists!")

        result_username = await self.session.execute(
            select(User).where(User.username == credentials.username)
        )
        if result_username.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail="User With This Username Exists!"
            )

        new_user = User(
            **credentials.model_dump(exclude={"email", "password"}),
            email=str(credentials.email),
            hashed_password=get_hashed_password(credentials.password),
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def login(self, email, password):
        try:
            if not email:
                raise HTTPException(status_code=400, detail="Email cannot be empty")

            result = await self.session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            access_token = create_access_token(
                {"sub": str(user.id), "role": user.role.value}
            )
            refresh_token = create_refresh_token(
                {"sub": str(user.id), "role": user.role.value}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        except HTTPException:
            raise
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database error during login")

    async def get_by_id(self, user_id: UUID):
        try:
            result = await self.session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=500, detail="Database error while fetching user"
            )

    async def refresh(self, request: Request):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise credentials_exception

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            payload = decode_token(token)
        except jwt.InvalidTokenError:
            raise credentials_exception

        if payload.get("type") != "refresh":
            raise credentials_exception

        user_creds = payload.get("sub")
        if not user_creds:
            raise credentials_exception

        user = await self.get_by_id(UUID(user_creds))
        if not user:
            raise credentials_exception

        new_access_token = create_access_token(
            {"sub": user_creds, "role": user.role.value}
        )
        return {"access_token": new_access_token, "token_type": "bearer"}

    async def update(self, user_id: UUID, user_data: UpdateUser):
        user = await self.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data_dict = user_data.model_dump(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(user, key, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user
