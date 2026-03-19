from modules.rag.vector_store import VectorDBService


async def retrieval_tool(query: str) -> str:
    '''A tool function that takes a query as input and returns relevant information retrieved from the vector database.'''
    vector_db = VectorDBService()
    return await vector_db.search(query)