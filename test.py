
from modules.rag.embeddings import EmbeddingService
from modules.rag.vector_store import VectorDBService
from dotenv import load_dotenv
import asyncio
import json
import httpx

load_dotenv("core/.env")

def test_embedding_service():
    embeddings = EmbeddingService.embed(document_folder="data")
    return embeddings

async def test_vector_store():
    documents = await EmbeddingService.aload_documents(document_folder="data", perform_chunk=True)
    result = await VectorDBService().aupsert_documents(documents=documents)
    return result


def parse_sse_event(line: str) -> dict | None:
    """Parse a single SSE data line into a dict."""
    if line.startswith("data: "):
        return json.loads(line[6:])
    return None

async def test_agent_streaming(base_url: str = "http://localhost:8001", query: str = "Tell me about Sayan", session_id: str = "test-session-001"):
    """Test streaming response from the agent endpoint, parsing ag-ui SSE events."""
    url = f"{base_url}/agent/query"
    body = {"query": query, "session_id": session_id}

    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", url, json=body) as response:
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}\n")

            async for line in response.aiter_lines():
                if line:
                    event_data = parse_sse_event(line)
                    if event_data and event_data.get("delta"):
                        content = event_data.get("delta")
                        print(content, end="", flush=True)
                        await asyncio.sleep(0.02)  # smooth out display

if __name__ == "__main__":

    # Test agent streaming response
    query = """
    Tell the story of Hindu mythology Mahabharata in 300 words. Include special events. DO NOT use previous message to make answer.
    """

    asyncio.run(test_agent_streaming(query=query, session_id="test-session-001"))

    
