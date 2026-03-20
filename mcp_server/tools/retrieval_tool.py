from modules.rag.vector_store import VectorDBService


async def retrieval_tool(query: str) -> str:
    '''
    Use this tool to retrieve all the information if the query asks for specific information.
    Input: A query string asking for information.
    Output: A string containing all the relevant information retrieved from the vector database.
    '''
    vector_db = VectorDBService()
    docs = await vector_db.search(query)
    return "\n\n---\n\n".join(doc.page_content for doc in docs)