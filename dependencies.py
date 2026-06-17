from fastapi import Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import LocalSession
from models import User
from auth import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_database():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_database)):
    
    decoded_data = verify_access_token(token)

    current_user: User = db.query(User).filter(User.id == decoded_data["sub"]).first()

    if current_user is None:
        raise HTTPException(401, "User does not exist.")

    return current_user