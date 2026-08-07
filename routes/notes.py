from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from models import User, Note
from dependencies import get_current_user, get_database
from schemas import NoteUpdate, NoteCreate, NoteResponse
from auth import encrypt, decrypt

router = APIRouter()

async def get_note_or_404(note_id: str, user: User, db: AsyncSession):

    result = await db.execute(select(Note).where(Note.id == note_id, Note.user_id == user.id))
    existing_note = result.scalar_one_or_none()
    
    if not existing_note:
        raise HTTPException(404, detail="Note not Found.")
    
    return existing_note


@router.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(note: NoteCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):

    enc_title = encrypt(note.title)
    enc_content = encrypt(note.content)

    new_note = Note(
        user_id=user.id,
        title=enc_title,
        content=enc_content,
    )

    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)

    return NoteResponse(
        id=new_note.id,
        title=note.title,
        content=note.content,
        created_at=new_note.created_at,
        updated_at=new_note.updated_at
    )

@router.get("/notes", response_model=list[NoteResponse], status_code=200)
async def read_notes(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_database)):

    result = await db.execute(select(Note).where(Note.user_id == user.id).offset(offset).limit(limit))
    notes = result.scalars().all()

    return [
        NoteResponse(
            id=note.id,
            title=decrypt(note.title),
            content=decrypt(note.content),
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        for note in notes
    ]

@router.get("/notes/{note_id}", response_model=NoteResponse, status_code=200)
async def read_one_note(note_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    db_note = await get_note_or_404(note_id, user, db)

    return NoteResponse(
        id=db_note.id,
        title=decrypt(db_note.title),
        content=decrypt(db_note.content),
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )

@router.patch("/notes/{note_id}", response_model=NoteResponse, status_code=200)
async def update_note(note_id: str, updated_note: NoteUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    
    existing_note = await get_note_or_404(note_id, user, db)

    update_data = updated_note.model_dump(exclude_unset=True)
    # Only update what user entered
    if not update_data:
        raise HTTPException(400, detail="No fields provided to update.")
    
    if "title" in update_data:
        existing_note.title = encrypt(update_data["title"])
    if "content" in update_data:
        existing_note.content = encrypt(update_data["content"])

    await db.commit()
    await db.refresh(existing_note)

    return NoteResponse(
        id=existing_note.id,
        title=decrypt(existing_note.title),
        content=decrypt(existing_note.content),
        created_at=existing_note.created_at,
        updated_at=existing_note.updated_at
    )

@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    existing_note = await get_note_or_404(note_id, user, db)
        
    await db.delete(existing_note)
    await db.commit()