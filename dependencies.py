from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import verify_access_token
from database import LocalSession
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def get_database() -> AsyncGenerator[AsyncSession]:
    async with LocalSession() as db:
        yield db


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_database)
) -> User:

    decoded_data = verify_access_token(token)

    result = await db.execute(select(User).where(User.id == decoded_data["sub"]))
    current_user = result.scalar_one_or_none()

    if current_user is None:
        raise HTTPException(401, "User does not exist.")

    return current_user
