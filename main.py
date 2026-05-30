from fastapi import FastAPI, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
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

def verify_access_token(token):
    try:
        decoded_jwt = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        return { "token_status": "valid", "data": decoded_jwt }
    except jwt.ExpiredSignatureError:
        return { "token_status": "invalid", "message": "Token has expired." }
    except jwt.InvalidTokenError:
        return { "token_status": "invalid", "message": "Token provided is invalid." }
        

pwHasher = PasswordHasher()
Base.metadata.create_all(engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

def get_database():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username, password, db):
    existing_user = db.query(User).filter(User.username == username).first()

    if not existing_user:
        raise HTTPException(401, "Invalid credentials.")

    try:
        pwHasher.verify(existing_user.password, password)
    except VerificationError:
        raise HTTPException(401, "Invalid credentials.")
    
    return existing_user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_database)):
    
    token_data = verify_access_token(token)

    if token_data["token_status"] != "valid":
        raise HTTPException(401, token_data["message"])
    
    current_user_id = token_data["data"]["sub"]

    current_user: User = db.query(User).filter(User.id == current_user_id).first()

    if current_user is None:
        raise HTTPException(401, "User does not exist.")

    return current_user



@app.get("/")
def read_root():
    return { "message": "Hello, welcome!\n To register here. Access /register to register. Once done, visit /login." }

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
    token = create_access_token(current_user.id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )