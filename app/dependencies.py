from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_token
from app.database import get_session
from app.services.auth import UserService

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDep):
    return UserService(session)


async def get_current_user(
    token=Depends(oauth_scheme), session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        # Reject refresh tokens used as access tokens
        if payload.get("type") not in ("access", None):
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user_service = UserService(session)
    user = await user_service.get_by_id(UUID(user_id))

    if user is None:
        raise credentials_exception

    return user


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
