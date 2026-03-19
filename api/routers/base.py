from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return JSONResponse(content={"status": "healthy"}, status_code=200)

