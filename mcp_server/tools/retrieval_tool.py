from modules.rag.vector_store import VectorDBService


async def retrieval_tool(query: str, top_k: int = 5, score_threshold: float = 0.5, search_type: str = "similarity_score_threshold", lambda_mult: float = 0.5) -> str:
    '''A tool function that takes a query as input and returns relevant information retrieved from the vector database.'''
    vector_db = VectorDBService()
    docs = await vector_db.search(query)
    return "\n\n---\n\n".join(doc.page_content for doc in docs)