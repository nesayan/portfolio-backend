from typing import Literal, Optional
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

    def _get_vector_store(self, collection_name: Optional[str] = None) -> QdrantVectorStore:
        '''Returns an instance of QdrantVectorStore connected to the specified collection in the vector database.'''

        if not collection_name:
            collection_name = settings.VECTOR_COLLECTION

        return QdrantVectorStore(
            client=self.client,
            collection_name= collection_name,
            embedding=EmbeddingService.embedding_model,
        )
    
    def _get_retriever(self, collection_name: Optional[str] = None, search_type: Literal["similarity", "similarity_score_threshold", "mmr"] = "similarity", search_kwargs: Optional[dict] = {"k": 5}):
        '''Returns a retriever instance for the specified collection in the vector database.'''

        if not collection_name:
            collection_name = settings.VECTOR_COLLECTION

        store = self._get_vector_store(collection_name)
        return store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

    def _collection_exists(self, collection_name: str) -> bool:
        '''Checks if a collection with the specified name exists in the vector database.'''

        return self.client.collection_exists(collection_name=collection_name)

    def create_collection_if_not_exists(self) -> None:
        '''Checks if the specified collection exists in the vector database, and creates it if it does not.'''

        is_collection_exist = self._collection_exists(settings.VECTOR_COLLECTION)

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


        store = self._get_vector_store()

        ids = [
            str(uuid5(NAMESPACE_URL, f"{doc.metadata.get('source', '')}:{doc.page_content}"))
            for doc in documents
        ]

        return await store.aadd_documents(documents, ids=ids)
    
    async def search(self, query: str, search_type: Literal["similarity", "similarity_score_threshold", "mmr"] = "similarity_score_threshold", score_threshold: float = 0.5, top_k: int = 5, lambda_mult: float = 0.5) -> list[Document]:
        '''Asynchronously searches the vector database for documents relevant to the query.'''

        if not self._collection_exists(settings.VECTOR_COLLECTION):
            raise ValueError(f"Collection '{settings.VECTOR_COLLECTION}' does not exist in the vector database.")
        
        if search_type not in ["similarity", "similarity_score_threshold", "mmr"]:
            raise ValueError(f"Invalid search type '{search_type}'. Valid options are 'similarity', 'similarity_score_threshold', and 'mmr'.")
        
        store = self._get_vector_store()

        if search_type == "similarity":
            results = await store.asimilarity_search_with_score(query, k=top_k)
            results.sort(key=lambda x: x[1], reverse=True)
            docs = []
            for doc, score in results:
                doc.id = doc.metadata.get("_id")
                doc.metadata["score"] = round(score, 4)
                docs.append(doc)
            return docs

        elif search_type == "similarity_score_threshold":
            results = await store.asimilarity_search_with_score(query, k=top_k)
            results.sort(key=lambda x: x[1], reverse=True)
            docs = []
            for doc, score in results:
                if score < score_threshold:
                    continue
                doc.id = doc.metadata.get("_id")
                doc.metadata["score"] = round(score, 4)
                docs.append(doc)
            return docs

        else:  # mmr
            docs = await store.amax_marginal_relevance_search(query, k=top_k, fetch_k=20, lambda_mult=lambda_mult)
            for doc in docs:
                doc.id = doc.metadata.get("_id")
            return docs
        

