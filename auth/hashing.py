from fastapi import HTTPException
from models import User
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.concurrency import run_in_threadpool

pwHasher = PasswordHasher()

async def authenticate_user(username: str, password: str, db: AsyncSession) -> User:
    clean_username = username.strip().lower()

    result = await db.execute(select(User).where(User.username == clean_username))
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(401, "Invalid credentials.")

    try:
        await run_in_threadpool(pwHasher.verify, existing_user.password, password)
    except VerificationError:
        raise HTTPException(401, "Invalid credentials.")
    
    return existing_user

async def hash_password(password: str) -> str:
    hashed_pw = await run_in_threadpool(pwHasher.hash, password)
    return hashed_pw