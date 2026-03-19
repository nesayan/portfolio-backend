from pathlib import Path
from typing import Literal
from fastapi import APIRouter, HTTPException, UploadFile, File
from api.schemas import GetEmbeddingsResponseList, CreateEmbeddingsResponseList

from modules.rag.embeddings import EmbeddingService
from modules.rag.vector_store import VectorDBService

from mcp_server.tools.retrieval_tool import retrieval_tool

from core.config import settings

DATA_DIR = Path(settings.DATA_DIR)


router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/get_embeddings", response_model=GetEmbeddingsResponseList)
async def get_embeddings(file: UploadFile = File(...)):
    '''Endpoint to get embeddings for a given PDF file without storing them in the vector database.'''
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    dest = DATA_DIR / file.filename

    contents = await file.read()
    dest.write_bytes(contents)

    embeddings = await EmbeddingService.aembed(document_folder=DATA_DIR, perform_chunk=True)

    Path(dest).unlink()

    return GetEmbeddingsResponseList(embeddings=embeddings, count=len(embeddings))


@router.post("/create_embeddings", response_model=CreateEmbeddingsResponseList)
async def create_embeddings(file: UploadFile = File(...)):
    '''Endpoint to create embeddings for a given PDF file and store them in the vector database.'''
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_DIR / file.filename

    contents = await file.read()
    dest.write_bytes(contents)

    try:
        documents = await EmbeddingService.aload_documents(document_folder=DATA_DIR, perform_chunk=True, chunk_size=200, chunk_overlap=50)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    finally:
        Path(dest).unlink()

    _ids = await VectorDBService().aupsert_documents(documents=documents)

    return CreateEmbeddingsResponseList(embedding_ids=_ids, count=len(_ids))

@router.post("/search")
async def search(query: str):
    '''Endpoint to search for relevant documents in the vector database based on a query.'''
    try:
        results = await retrieval_tool(query=query, top_k=top_k, score_threshold=score_threshold, search_type=search_type, lambda_mult=lambda_mult)
        return {"tool_results": results}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
