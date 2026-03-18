
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI

from core.config import settings
from api import api_router  


def setup():
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    yield


app = FastAPI(
    title="Agentic RAG Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)
