from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, LocalSession, Base
from models import User
from schemas import UserCreate, UserInDB
from argon2 import PasswordHasher

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
        raise HTTPException(401, detail="Username is already taken.")

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


