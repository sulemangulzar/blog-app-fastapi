from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.core.security import oauth_scheme
from app.src.database.database import get_session
from app.src.database.redis import check_jti_in_blacklist
from app.src.models.blog import UserInfo
from app.src.services.blog import BlogService
from app.src.services.user import UserService
from app.src.utils import decode_token

sessionDep = Annotated[AsyncSession, Depends(get_session)]


# Access Token
async def get_access_token(token: Annotated[str, Depends(oauth_scheme)]):
    data = decode_token(token)
    jti = data.get("jti") if data else None
    if data is None or jti is None or await check_jti_in_blacklist(jti):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return data


# Logged IN User
async def get_current_user(
    token_data: Annotated[dict, Depends(get_access_token)], session: sessionDep
):
    return await session.get(UserInfo, token_data["user"]["id"])


def get_blog_service(session: sessionDep):
    return BlogService(session)


def get_user_service(session: sessionDep):
    return UserService(session)


serviceDep = Annotated[BlogService, Depends(get_blog_service)]
userServiceDep = Annotated[UserService, Depends(get_user_service)]
userDep = Annotated[UserInfo, Depends(get_current_user)]
