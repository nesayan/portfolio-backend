''' LangGraph agent that connects to MCP server for tools'''

from langgraph.graph import StateGraph, START, END
from langchain.tools import ToolNode
from langchain.tools.tool_node import tools_condition
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from core.config import settings
from langchain_groq.chat_models import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    answer: str


_graph = None


def build_graph():

    mcp_client = MultiServerMCPClient(
        {
            "retrieval_mcp_server": {
                "url": f"http://localhost:{settings.PORT}/mcp",
                "transport": "streamable_http",
            }
        }
    )
    tools = mcp_client.get_tools()

    def llm_with_tools():
        llm = ChatGroq(model=settings.LLM_MODEL, temperature=0, streaming=True)
        return llm.bind_tools(tools=tools)

    workflow = StateGraph(State)
    workflow.add_node("llm", llm_with_tools)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "llm")
    workflow.add_conditional_edges(
        "llm",
        tools_condition,  # Routes to "tools" or "__end__"
        {"tools": "tools", "__end__": END}
    )
    workflow.add_edge("tools", "llm")

    graph = workflow.compile(checkpointer=InMemorySaver())

    return graph


def get_graph():
    """Lazy init — builds the graph on first call, when the app is already serving."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


