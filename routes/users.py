from fastapi import Depends, HTTPException, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import User
from dependencies import get_current_user, get_database
from schemas import UserCreate, UserResponse, TokenResponse
from auth import hash_password, authenticate_user, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_database)):
    hashed_password = hash_password(user.password)

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user is not None:
        raise HTTPException(409, detail="Username is already taken.")

    new_user = User(
        username=user.username,
        password=hashed_password,
        fname=user.name.fname,
        sname=user.name.sname,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        name = {
            "fname": new_user.fname,
            "sname": new_user.sname
        }
    )

@router.post("/login", response_model=TokenResponse, status_code=200)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_database)):
    current_user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(current_user.id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )

@router.get("/users/me", response_model=UserResponse, status_code=200)
def read_users_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        username=user.username,
        name= {
            "fname": user.fname,
            "sname": user.sname
        }
    )