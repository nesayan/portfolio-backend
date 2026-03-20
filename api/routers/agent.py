
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from modules.agents.agent import get_graph
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from ag_ui.core import TextMessageChunkEvent, EventType
from ag_ui.encoder import EventEncoder


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query")
async def query_agent(query: str):
    '''Endpoint to send a query to the agent and receive a response.'''

    event_encoder = EventEncoder()

    async def astream_response(graph: CompiledStateGraph, state, config: RunnableConfig):
        async for chunk, metadata in graph.astream(state, config=config, stream_mode="messages"):
 
            if metadata.get('langgraph_node') == "llm":
                if chunk and chunk.content:
                    event = TextMessageChunkEvent(
                        type=EventType.TEXT_MESSAGE_CHUNK,
                        delta=chunk.content,
                    )
                    yield event_encoder.encode(event)

            
    
    graph = await get_graph()
    state = {"messages": [HumanMessage(content=query)]}
    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    return StreamingResponse(astream_response(graph, state, config=config), media_type=event_encoder.get_content_type())
