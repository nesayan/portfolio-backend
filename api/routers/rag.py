from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from api.schemas import GetEmbeddingsResponseList, CreateEmbeddingsResponseList

from modules.rag.embeddings import EmbeddingService
from modules.rag.vector_store import VectorDBService

from mcp_server.tools.retrieval_tool import retrieval_tool

from core.config import settings
from core.logger import logger

DATA_DIR = Path(settings.DATA_DIR)


router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/get_embeddings", response_model=GetEmbeddingsResponseList)
async def get_embeddings(file: UploadFile = File(...), perform_chunk: bool = True, chunk_size: int = 200, chunk_overlap: int = 50):
    '''Endpoint to get embeddings for a given PDF file without storing them in the vector database.'''
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    dest = DATA_DIR / file.filename

    contents = await file.read()
    dest.write_bytes(contents)

    try:
        embeddings = await EmbeddingService.aembed(document_folder=DATA_DIR, perform_chunk=perform_chunk, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    except Exception as e:
        logger.error(f"Error getting embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(dest).unlink()

    return GetEmbeddingsResponseList(embeddings=embeddings, count=len(embeddings))


@router.post("/create_embeddings", response_model=CreateEmbeddingsResponseList)
async def create_embeddings(file: UploadFile = File(...), force_recreate: bool = False, perform_chunk: bool = True, chunk_size: int = 200, chunk_overlap: int = 50):
    '''Endpoint to create embeddings for a given PDF file and store them in the vector database.'''
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_DIR / file.filename

    contents = await file.read()
    dest.write_bytes(contents)

    try:
        documents = await EmbeddingService.aload_documents(document_folder=DATA_DIR, perform_chunk=perform_chunk, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(dest).unlink()

    try:
        _ids = await VectorDBService().aupsert_documents(documents=documents, force_recreate=force_recreate)
    except Exception as e:
        logger.error(f"Error upserting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    return CreateEmbeddingsResponseList(embedding_ids=_ids, count=len(_ids))

@router.post("/search")
async def search(query: str):
    '''Endpoint to search for relevant documents in the vector database based on a query.'''
    try:
        results = await retrieval_tool(query=query)
        return {"tool_results": results}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collection/exists")
async def collection_exists(collection_name: Optional[str] = None):
    '''Endpoint to check if the vector store collection exists.'''
    db = VectorDBService()
    if not collection_name:
        collection_name = settings.VECTOR_COLLECTION
    exists = db._collection_exists(collection_name)
    return {"collection": collection_name, "exists": exists}
