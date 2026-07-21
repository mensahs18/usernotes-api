from fastapi import Depends, HTTPException, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from dependencies import get_current_user, get_database
from schemas import UserCreate, UserResponse, TokenResponse
from auth import hash_password, authenticate_user, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_database)):
    hashed_password = await hash_password(user.password)

    new_user = User(
        username=user.username,
        password=hashed_password,
        fname=user.name.fname,
        sname=user.name.sname,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError: #Race condition has caused repeat, db unique=true, raises IntegrityError
        await db.rollback()
        raise HTTPException(409, detail="Username is already taken")

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        name = {
            "fname": new_user.fname,
            "sname": new_user.sname
        }
    )

@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_database)):
    current_user = await authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(current_user.id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )

@router.get("/me", response_model=UserResponse, status_code=200)
async def read_users_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        username=user.username,
        name= {
            "fname": user.fname,
            "sname": user.sname
        }
    )