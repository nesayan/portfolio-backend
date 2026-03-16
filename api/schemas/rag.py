from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    query: str = Field(..., description="The query to be processed.", min_length=1)


class RagQueryResponse(BaseModel):
    query: str = Field(..., description="The original query.")
    answer: str = Field(..., description="The generated answer to the query.")
    sources: list[str] = Field(..., description="The sources used to generate the answer.")


class EmbeddingResponse(BaseModel):
    embedding: list[float] = Field(..., description="A single embedding vector.")


class GetEmbeddingsResponseList(BaseModel):
    count: int = Field(..., description="Total number of embeddings.")
    embeddings: list[EmbeddingResponse] = Field(..., description="List of embedding responses.")


class CreateEmbeddingsResponseList(BaseModel):
    count: int = Field(..., description="Total number of embeddings upserted.")
    embedding_ids: list[str] = Field(..., description="List of embedding IDs upserted into the database.")