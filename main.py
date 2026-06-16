from fastapi import FastAPI, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, LocalSession, Base
from models import User, Note
from schemas import UserCreate, UserResponse, NoteUpdate, TokenPayload, TokenResponse, NoteCreate, NoteResponse
from auth import hash_password, authenticate_user
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
        sub=str(user_id),
        iat=int(now.timestamp()),
        exp=int(expiry_time.timestamp())
        )
    
    encoded_jwt = jwt.encode(payload=token_payload.model_dump() , key=SECRET_KEY , algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token):
    try:
        decoded_jwt = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return { "token_status": "valid", "data": decoded_jwt }
    except jwt.ExpiredSignatureError:
        raise HTTPException( 401, "Token has expired." )
    except jwt.InvalidTokenError:
        raise HTTPException( 401, "Token is invalid." )
        

Base.metadata.create_all(engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

def get_database():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_database)):
    
    decoded_data = verify_access_token(token)

    current_user: User = db.query(User).filter(User.id == decoded_data["data"]["sub"]).first()

    if current_user is None:
        raise HTTPException(401, "User does not exist.")

    return current_user

def get_note_or_404(note_id, user, db):
    existing_note = db.query(Note).filter(Note.id == note_id).first()

    if not existing_note:
        raise HTTPException(404, detail="Note not Found.")
    
    if not existing_note.user_id == user.id:
        raise HTTPException(404, detail="Note not Found.")
    return existing_note

@app.get("/", status_code=200)
def read_root():
    return { "message": "API is successfully running." }

@app.post("/register", response_model=UserResponse, status_code=201)
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

@app.post("/login", response_model=TokenResponse, status_code=200)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_database)):
    current_user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(current_user.id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )

@app.get("/users/me", response_model=UserResponse, status_code=200)
def read_users_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        username=user.username,
        name= {
            "fname": user.fname,
            "sname": user.sname
        }
    )

@app.post("/notes", response_model=NoteResponse, status_code=201)
def create_note(note: NoteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    new_note = Note(
        user_id=user.id,
        title=note.title,
        content=note.content,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note

@app.get("/notes", response_model=list[NoteResponse], status_code=200)
def read_notes(user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return db.query(Note).filter(Note.user_id == user.id).all()

@app.get("/notes/{note_id}", response_model=NoteResponse, status_code=200)
def read_one_note(note_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_database)):

    existing_note = get_note_or_404(note_id, user, db)
    
    return NoteResponse(
        id=existing_note.id,
        title=existing_note.title,
        content=existing_note.content,
        created_at=existing_note.created_at,
        updated_at=existing_note.updated_at
    )

@app.patch("/notes/{note_id}", response_model=NoteResponse, status_code=200)
def update_note(note_id: str, updated_note: NoteUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    
    existing_note = get_note_or_404(note_id, user, db)

    if updated_note.title is None and updated_note.content is None:
        raise HTTPException(400, detail="No fields provided to update.")
    
    if updated_note.title is not None:
        existing_note.title = updated_note.title
    if updated_note.content is not None:
        existing_note.content = updated_note.content

    db.commit()
    db.refresh(existing_note)

    return existing_note

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    existing_note = get_note_or_404(note_id, user, db)
    
    title = existing_note.title
    
    db.delete(existing_note)
    db.commit()

    return { "message": f"Note '{title}' successfully deleted"}