from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import engine, Base
from routes import user_router, note_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/", status_code=200, tags=["root"])
def read_root():
    return { "message": "API is successfully running." }

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(note_router, tags=["notes"])

