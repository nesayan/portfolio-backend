''' LangGraph agent that connects to MCP server for tools'''

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from core.config import settings
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage

SYSTEM_PROMPT = """
You are an assistant for a portfolio website. Your task is to help users understand the candidate's profile based on the information provided.
You have access to a tools by MCP server. Prefer to use tools you are provided with.
Instructions:
    1. If it is a general question, no need to use tools, answer based on the information you have.
    2. If the question is specific and requires more information, use the retrieval tool to get the relevant information
Output Instructions:
    - Always answer in a professional manner, providing relevant information without unnecessary details.
"""


class State(TypedDict):
    messages: Annotated[list, add_messages]


_graph = None


async def build_graph():

    mcp_client = MultiServerMCPClient(
        {
            "retrieval_mcp_server": {
                "url": f"http://localhost:{settings.PORT}/mcp",
                "transport": "http",
            }
        }
    )
    tools = await mcp_client.get_tools()

    llm = settings.get_llm(provider=settings.DEFAULT_LLM_PROVIDER)
    llm_with_tools = llm.bind_tools(tools=tools)

    async def llm_node(state: State):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # Tool Node
    tools_node = ToolNode(tools)

    # Workflow - defines the flow of the agent
    workflow = StateGraph(State)
    workflow.add_node("llm", llm_node)
    workflow.add_node("tools", tools_node)

    workflow.add_edge(START, "llm")
    workflow.add_conditional_edges(
        "llm",
        tools_condition,  # Routes to "tools" or "__end__"
        {"tools": "tools", "__end__": END}
    )
    workflow.add_edge("tools", "llm")

    graph = workflow.compile(checkpointer=InMemorySaver())

    return graph


async def get_graph():
    """Lazy init — builds the graph on first call, when the app is already serving."""
    global _graph
    if _graph is None:
        _graph = await build_graph()
    return _graph


