from fastapi import FastAPI
from database import engine, Base
from routes import user_router, note_router

Base.metadata.create_all(engine)

app = FastAPI()

@app.get("/", status_code=200, tags=["root"])
def read_root():
    return { "message": "API is successfully running." }

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(note_router, tags=["notes"])

