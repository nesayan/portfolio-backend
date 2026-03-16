from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return JSONResponse(content={"message": "Agentic RAG backend is running"}, status_code=200)


@router.get("/health")
def health() -> dict[str, str]:
    return JSONResponse(content={"status": "healthy"}, status_code=200)

