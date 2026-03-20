''' LangGraph agent that connects to MCP server for tools'''

from langgraph.graph import StateGraph, START, END
from langchain.tools import ToolNode
from langchain.tools.tool_node import tools_condition
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

import os
from core.config import settings
from langchain_groq.chat_models import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    answer: str


def build_graph():

    mcp_client = MultiServerMCPClient(
        {
            "retrieval_mcp_server": {
                "url": f"http://localhost:{os.getenv('PORT')}/mcp",
                "transport": "streamable_http",
            }
        }
    )
    tools=[]

    def llm_with_tools():
        llm = ChatGroq(model=settings.LLM_MODEL, temperature=0, streaming=True)
        return llm.bind_tools(tools=tools)

    


    graph = StateGraph(State)
    graph.add_node("llm", llm_with_tools)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "llm")
    graph.add_conditional_edges(
        "llm",
        tools_condition,  # Routes to "tools" or "__end__"
        {"tools": "tools", "__end__": END}
    )
    graph.add_edge("tools", "llm")

    return graph.compile(checkpointer=InMemorySaver())


