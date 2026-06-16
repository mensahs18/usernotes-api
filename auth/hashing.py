from fastapi import HTTPException
from models import User
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError


pwHasher = PasswordHasher()

def authenticate_user(username, password, db):
    existing_user = db.query(User).filter(User.username == username).first()

    if not existing_user:
        raise HTTPException(401, "Invalid credentials.")

    try:
        pwHasher.verify(existing_user.password, password)
    except VerificationError:
        raise HTTPException(401, "Invalid credentials.")
    
    return existing_user

def hash_password(password):
    return pwHasher.hash(password)