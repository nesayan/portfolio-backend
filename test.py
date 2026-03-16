from modules.rag.embeddings import EmbeddingService
from modules.rag.vector_store import VectorDBService
from dotenv import load_dotenv
import asyncio

load_dotenv("core/.env")

def test_embedding_service():
    embeddings = EmbeddingService.embed(document_folder="data")
    return embeddings

async def test_vector_store():
    documents = await EmbeddingService.aload_documents(document_folder="data", perform_chunk=True)
    result = await VectorDBService().aupsert_documents(documents=documents)
    return result

if __name__ == "__main__":

    # test_vector_store()
    e = asyncio.run(test_vector_store())
    print(e)