from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.database.database import get_session
from app.src.services.blog import BlogService
from app.src.services.user import UserService

sessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_blog_service(session: sessionDep):
    return BlogService(session)


def get_user_service(session: sessionDep):
    return UserService(session)


serviceDep = Annotated[BlogService, Depends(get_blog_service)]
userServiceDep = Annotated[UserService, Depends(get_user_service)]
