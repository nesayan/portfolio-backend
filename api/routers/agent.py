

from typing import Literal
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.config import settings
from modules.agents.agent import get_graph
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import RunnableConfig


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query")
async def query_agent(query: str, enable_async: Literal["true", "false"] = "true"):
    '''Endpoint to send a query to the agent and receive a response.'''


    async def astream_response(graph: CompiledStateGraph, state: dict, config: RunnableConfig):
        async for chunk, metadata in graph.astream(state, config=config, stream_mode="messages", version="v2"):
            print(metadata, end="\n\n")
            yield chunk

    def stream_response(graph: CompiledStateGraph, state: dict, config: RunnableConfig):
        for chunk, metadata in graph.stream(state, config=config, stream_mode="messages", version="v2"):
            print(metadata, end="\n\n")
            yield chunk
    
    graph = get_graph()
    state = {"query": query}
    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    if enable_async == "true":
        return StreamingResponse(astream_response(graph, state, config=config), media_type="text/event-stream")
    return StreamingResponse(stream_response(graph, state, config=config), media_type="text/event-stream")

    
