import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

import pytest  # noqa: E402
from fastmcp.client import Client  # noqa: E402

from mcp_server.server import mcp  # noqa: E402


@pytest.mark.anyio
async def test_mcp_connection():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("Available tools:", tools)
        assert len(tools) > 0


