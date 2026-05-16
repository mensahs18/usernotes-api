from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, LocalSession, Base
from models import User
from schemas import UserCreate, LoginRequest, TokenPayload, TokenResponse
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import jwt

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(user_id):
    now = datetime.now(timezone.utc)
    expiry_time = now + timedelta(minutes=15)

    token_payload = TokenPayload(
        sub=user_id,
        iat=now,
        exp=expiry_time
        )
    
    encoded_jwt = jwt.encode(payload=token_payload.model_dump() , key=SECRET_KEY , algorithm=ALGORITHM)

    return encoded_jwt

pwHasher = PasswordHasher()
Base.metadata.create_all(engine)

app = FastAPI()

def get_database():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return { "message": "Hello, Users!\n", "users" : "There are users here. Access /users to view them." }

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_database)):
    hashed_password = pwHasher.hash(user.password)

    existing_user = db.query(User).filter(User.username == user.username).first()
    if (existing_user != None):
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

    return { "message": f"Registration successful.\nWelcome, {new_user.fname}.", "user_id:" : new_user.id,  }

@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_database)):
    current_user = authenticate_user(user.username, user.password, db)
    
    return { "message": f"Welcome back, {current_user.fname}."}

def authenticate_user(username, password, db):
    existing_user = db.query(User).filter(User.username == username).first()

    if not existing_user:
        raise HTTPException(401, "Invalid credentials.")

    try:
        pwHasher.verify(existing_user.password, password)
    except VerificationError:
        raise HTTPException(401, "Invalid credentials.")
    
    return existing_user