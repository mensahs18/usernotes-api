from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, LocalSession, Base
from models import User
from schemas import UserCreate

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

@app.get("/register")
def register(user: UserCreate, db: Session = Depends(get_database)):
    
    new_user = User(
        username=user.username,
        password=user.password,
        fname=user.fname,
        sname=user.sname,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return { "message": f"Registration successful.\nWelcome, {new_user.fname}.", "user_id:" : f"{new_user.id}",  }


