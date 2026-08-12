from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

strippedStr = Annotated[str, StringConstraints(strip_whitespace=True)]

class NoteCreate(BaseModel):
    title: strippedStr = Field(min_length=1, max_length=200)
    content: strippedStr = Field(min_length=1, max_length=100000)

class NoteUpdate(BaseModel):
    title: strippedStr | None = Field(default=None, min_length=1, max_length=200)
    content: strippedStr | None = Field(default=None, min_length=1, max_length=100000)

class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

class NotePreviewResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

class PaginatedNoteResponse(BaseModel):
    total: int
    limit: int
    offset: int
    notes: list[NotePreviewResponse]
