from fastapi import FastAPI
from database import engine, Base
from routes import user_router, note_router

Base.metadata.create_all(engine)

app = FastAPI()

@app.get("/", status_code=200)
def read_root():
    return { "message": "API is successfully running." }

app.include_router(user_router)
app.include_router(note_router)

