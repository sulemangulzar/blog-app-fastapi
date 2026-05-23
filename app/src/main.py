from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.src.database.database import create_all_tables
from app.src.routers.routers import master_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(master_router)
