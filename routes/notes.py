from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from models import User, Note
from dependencies import get_current_user, get_database
from schemas import NoteUpdate, NoteCreate, NoteResponse

router = APIRouter()

def get_note_or_404(note_id, user, db):
    existing_note = db.query(Note).filter(Note.id == note_id).first()

    if not existing_note:
        raise HTTPException(404, detail="Note not Found.")
    
    if not existing_note.user_id == user.id:
        raise HTTPException(404, detail="Note not Found.")
    return existing_note


@router.post("/notes", response_model=NoteResponse, status_code=201)
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

@router.get("/notes", response_model=list[NoteResponse], status_code=200)
def read_notes(user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return db.query(Note).filter(Note.user_id == user.id).all()

@router.get("/notes/{note_id}", response_model=NoteResponse, status_code=200)
def read_one_note(note_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_database)):

    existing_note = get_note_or_404(note_id, user, db)
    
    return existing_note

@router.patch("/notes/{note_id}", response_model=NoteResponse, status_code=200)
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

@router.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    existing_note = get_note_or_404(note_id, user, db)
    
    title = existing_note.title
    
    db.delete(existing_note)
    db.commit()

    return { "message": f"Note '{title}' successfully deleted"}