
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.schemas.agent import AgentQueryRequest
from modules.agents.agent import get_graph
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from ag_ui.core import TextMessageChunkEvent, EventType
from ag_ui.encoder import EventEncoder


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query")
async def query_agent(body: AgentQueryRequest):
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

            # if metadata.get('langgraph_node') == "tools":
            #     thread_id = metadata.get("thread_id")
            #     print("[DEBUG] Tool output for thread_id %s is: %s".format(thread_id, chunk))

            

            
    
    graph = await get_graph()
    state = {"messages": [HumanMessage(content=body.query)]}
    config: RunnableConfig = {"configurable": {"thread_id": body.session_id}}

    return StreamingResponse(astream_response(graph, state, config=config), media_type=event_encoder.get_content_type())
