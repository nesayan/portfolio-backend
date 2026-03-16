from pathlib import Path
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from api.dependencies import verify_basic_auth
from api.schemas import GetEmbeddingsResponseList, CreateEmbeddingsResponseList

from modules.rag.embeddings import EmbeddingService
from modules.rag.vector_store import VectorDBService

DATA_DIR = Path(os.getenv("DATA_DIR"))


router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/get_embeddings", response_model=GetEmbeddingsResponseList)
async def get_embeddings(file: UploadFile = File(...), _: str = Depends(verify_basic_auth)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    dest = DATA_DIR / file.filename

    contents = await file.read()
    dest.write_bytes(contents)

    embeddings = await EmbeddingService.aembed(document_folder=DATA_DIR, perform_chunk=True)

    Path(dest).unlink()

    return GetEmbeddingsResponseList(embeddings=embeddings, count=len(embeddings))


@router.post("/create_embeddings", response_model=CreateEmbeddingsResponseList)
async def create_embeddings(file: UploadFile = File(...), _: str = Depends(verify_basic_auth)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_DIR / file.filename

    contents = await file.read()
    dest.write_bytes(contents)

    documents = await EmbeddingService.aload_documents(document_folder=DATA_DIR, perform_chunk=True)

    Path(dest).unlink()

    _ids = await VectorDBService().aupsert_documents(documents=documents)

    return CreateEmbeddingsResponseList(embedding_ids=_ids, count=len(_ids))

