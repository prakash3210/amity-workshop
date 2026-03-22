# ============================================================
# clientstandalone.py — Hello World MCP Client (standalone)
# Connects to an already-running MCP server over HTTP. Does NOT
# start the server; you must run server_standalone.py first.
#
# Usage:
#   Terminal 1: python server_standalone.py
#   Terminal 2: python clientstandalone.py
# ============================================================

import asyncio

from mcp import ClientSession

try:
    from mcp.client.streamable_http import streamable_http_client
except ImportError:
    from mcp.client.streamable_http import streamablehttp_client as streamable_http_client

# URL where server_standalone.py is listening
MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    """Connect to the running MCP server over HTTP, list tools, and call them."""

    # Connect to the server (no subprocess — server must already be running)
    async with streamable_http_client(MCP_SERVER_URL) as (read_stream, write_stream, _get_session_id):

        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()
            print("✅ Connected to MCP server!\n")

            # Discover available tools
            tools_response = await session.list_tools()
            print("🔧 Available tools:")
            for tool in tools_response.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()

            # Call say_hello with no arguments
            print("📞 Calling say_hello() with no arguments...")
            result = await session.call_tool(name="say_hello", arguments={})
            for block in result.content:
                print(f"   Server replied: {block.text}")
            print()

            # Call say_hello with name
            print("📞 Calling say_hello(name='Prakash')...")
            result2 = await session.call_tool(
                name="say_hello",
                arguments={"name": "Prakash"},
            )
            for block in result2.content:
                print(f"   Server replied: {block.text}")
            print()

            # Call get_time
            print("📞 Calling get_time()...")
            result = await session.call_tool(name="get_time", arguments={})
            for block in result.content:
                print(f"   Server replied: {block.text}")
            print()

            print("🎉 Done! Standalone client and server are working.")


if __name__ == "__main__":
    asyncio.run(main())
