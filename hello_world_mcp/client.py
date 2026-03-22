# ============================================================
# client.py — Hello World MCP Client
# This script launches server.py as a subprocess, connects to
# it via the MCP protocol over STDIO, and calls the "say_hello"
# tool twice to demonstrate how everything fits together.
# ============================================================

import asyncio                    # Async runtime — same as on the server side
import sys                        # Used to detect the current Python interpreter path

# ClientSession manages the full lifecycle of an MCP connection:
# handshake, capability exchange, tool calls, cleanup.
from mcp import ClientSession

# StdioServerParameters tells the client HOW to launch the server:
# which executable to run and what arguments to pass.
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    """Connect to the MCP server, list its tools, and call say_hello."""

    # ── 1. Describe how to start the server ────────────────────
    # We tell the MCP client to launch `python server.py` as a
    # child process.  The client will open a pipe to that process's
    # stdin/stdout and speak the MCP protocol over it.
    server_params = StdioServerParameters(
        command=sys.executable,   # Use the SAME Python that's running this script
        args=["server.py"],       # Arguments passed to that Python process
        env=None,                 # Inherit the current environment variables
    )

    # ── 2. Open the connection ──────────────────────────────────
    # `stdio_client` is an async context-manager that:
    #   • spawns the server subprocess
    #   • returns (read_stream, write_stream) connected to its stdio
    # When the `async with` block exits, the subprocess is terminated.
    async with stdio_client(server_params) as (read_stream, write_stream):

        # ── 3. Start a ClientSession ────────────────────────────
        # ClientSession wraps the raw streams and gives us friendly
        # methods like .list_tools() and .call_tool().
        async with ClientSession(read_stream, write_stream) as session:

            # Perform the MCP handshake: the client sends `initialize`,
            # the server replies with its capabilities, then the client
            # confirms with `initialized`.  All of this happens here.
            await session.initialize()
            print("✅ Connected to MCP server!\n")

            # ── 4. Discover available tools ─────────────────────
            # Ask the server "what tools do you expose?"
            tools_response = await session.list_tools()

            print("🔧 Available tools:")
            for tool in tools_response.tools:
                # Each tool has a name and a description we can print
                print(f"  • {tool.name}: {tool.description}")
            print()

            # ── 5. Call the tool — default greeting ─────────────
            # We invoke "say_hello" without arguments so it defaults
            # to greeting "World".
            print("📞 Calling say_hello() with no arguments...")
            result = await session.call_tool(
                name="say_hello",   # Must match the tool name on the server
                arguments={},       # Empty dict → use server-side defaults
            )

            # `result.content` is a list of content blocks (text, images, etc.)
            # We iterate and print every TextContent block.
            for block in result.content:
                print(f"   Server replied: {block.text}")
            print()

            # ── 6. Call the tool — personalised greeting ────────
            # Now we pass a "name" argument to personalise the greeting.
            print("📞 Calling say_hello(name='Prakash')...")
            result2 = await session.call_tool(
                name="say_hello",
                arguments={"name": "Prakash"},  # Server will use this value
            )

            for block in result2.content:
                print(f"   Server replied: {block.text}")
            print()

            # ── 7. Call get_time ─────────────────────────────────
            print("📞 Calling get_time()...")
            result = await session.call_tool(name="get_time", arguments={})
            for block in result.content:
                print(f"   Server replied: {block.text}")
            print()

            print("🎉 Done! Your first MCP server and client are working.")


# Only run when executed directly (not imported)
if __name__ == "__main__":
    asyncio.run(main())   # Kick off the async event loop
