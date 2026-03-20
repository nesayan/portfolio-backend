from fastmcp import FastMCP
from fastmcp.tools import Tool

from mcp_server.tools.retrieval_tool import retrieval_tool

mcp = FastMCP(__name__)

tools = [
    Tool.from_function(retrieval_tool, name="retrieval_tool")
]

for tool in tools:
    mcp.add_tool(tool)

