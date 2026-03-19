import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastmcp.utilities.lifespan import combine_lifespans

from core.config import settings
from api import api_router

from mcp_server.server import mcp


def setup():
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    yield


mcp_app = mcp.http_app(path='/')

app = FastAPI(
    title="Agentic RAG Backend",
    version="0.1.0",
    lifespan=combine_lifespans(lifespan, mcp_app.lifespan),
)

app.include_router(api_router)

app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
