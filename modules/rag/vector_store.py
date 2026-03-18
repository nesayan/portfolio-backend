from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document
from modules.rag.embeddings import EmbeddingService
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from core.config import settings

class VectorDBService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    def create_collection_if_not_exists(self) -> None:
        '''Checks if the specified collection exists in the vector database, and creates it if it does not.'''

        is_collection_exist = self.client.collection_exists(collection_name=settings.VECTOR_COLLECTION)

        if not is_collection_exist:
            size = EmbeddingService.embedding_model._client.get_sentence_embedding_dimension()
            distance = Distance.COSINE

            self.client.create_collection(
                collection_name=settings.VECTOR_COLLECTION,
                vectors_config=VectorParams(size=size, distance=distance),
            )

    async def aupsert_documents(self, documents: list[Document]) -> list[str]:
        '''Asynchronously upserts documents into the vector database after generating embeddings.'''

        self.create_collection_if_not_exists()

        store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.VECTOR_COLLECTION,
            embedding=EmbeddingService.embedding_model,
        )

        ids = [
            str(uuid5(NAMESPACE_URL, f"{doc.metadata.get('source', '')}:{doc.page_content}"))
            for doc in documents
        ]

        return await store.aadd_documents(documents, ids=ids)


