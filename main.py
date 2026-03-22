import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastmcp.utilities.lifespan import combine_lifespans
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import logger
from api.routers import base, rag, agent

from mcp_server.server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings._load_models()
    yield

    logger.info("Shutting down...")


mcp_app = mcp.http_app(path='/')

app = FastAPI(
    title="Agentic RAG Backend",
    version="0.1.0",
    lifespan=combine_lifespans(lifespan, mcp_app.lifespan),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base.router)
app.include_router(rag.router)
app.include_router(agent.router)

app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.PORT))
