from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
from routes import note_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/", status_code=200, tags=["root"])
def read_root() -> dict[str, str]:
    return { "message": "API is successfully running." }

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(note_router, tags=["notes"])

