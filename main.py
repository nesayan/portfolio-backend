
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI

load_dotenv("core/.env")
from api import api_router  # noqa: E402


def setup():
    Path(os.getenv("DATA_DIR")).mkdir(parents=True, exist_ok=True)


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
