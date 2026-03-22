# ============================================================
# server.py — Hello World MCP Server
# MCP (Model Context Protocol) lets you expose "tools" that
# AI models (or any client) can discover and call over a
# standard protocol.  The transport used here is STDIO, which
# means the client launches this script as a subprocess and
# communicates over stdin / stdout.
# ============================================================

# asyncio is Python's built-in library for writing async code.
# MCP servers are async by nature because they wait for requests.
import asyncio
import json
import sys
from datetime import datetime

# `mcp.server` provides the high-level Server class that handles
# the MCP handshake, capability negotiation, and message routing.
from mcp.server import Server

# `stdio_server` is a context-manager that wires up stdin/stdout
# as the transport layer so our server can talk to any MCP client.
from mcp.server.stdio import stdio_server

# These types describe the *shape* of the data we send back to
# the client when listing tools and when returning tool results.
from mcp.types import Tool, TextContent

# ── 1. Create the server instance ──────────────────────────────
# The string "hello-world-server" is the server's name; clients
# can read this during the initial handshake.
app = Server("hello-world-server")


# ── 2. Register the "list_tools" handler ───────────────────────
# Whenever a client asks "what tools do you have?", MCP calls
# the function decorated with @app.list_tools().
# It must return a list of Tool objects describing each tool.
@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the catalogue of tools this server exposes."""

    return [
        Tool(
            # Unique name the client uses to call this tool
            name="say_hello",

            # Human-readable description shown in UIs / to the LLM
            description="Returns a friendly Hello World greeting. "
                        "Optionally personalise it with a name.",

            # JSON Schema that describes the tool's input parameters.
            # The client (or LLM) uses this schema to know what to send.
            inputSchema={
                "type": "object",          # The input is a JSON object
                "properties": {
                    "name": {
                        "type": "string",  # The "name" field must be a string
                        "description": "The name to greet (default: World)",
                    }
                },
                # No required fields — "name" is optional
                "required": [],
            },
        ),
        Tool(
            name="get_time",
            description="Returns the current date and time in ISO format.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


# ── 3. Register the "call_tool" handler ────────────────────────
# When the client actually *calls* a tool, MCP routes the request
# here.  We receive the tool name and a dict of arguments.
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute the requested tool and return its result."""

    # Log the incoming tool request to console (stderr so stdout stays clean for MCP)
    request = {"name": name, "arguments": arguments}
    print("REQUEST", json.dumps(request, indent=2), file=sys.stderr)

    # Check which tool was requested by name
    if name == "say_hello":

        # Pull the optional "name" argument; default to "World"
        who = arguments.get("name", "World")

        # Build the greeting string
        greeting = f"Hello, {who}! 👋 Welcome to your first MCP server!"

        # Return a list of content blocks.  TextContent wraps plain text.
        # MCP supports other content types (images, resources, etc.) too.
        result = [TextContent(type="text", text=greeting)]

    elif name == "get_time":
        now = datetime.now().isoformat()
        result = [TextContent(type="text", text=f"Current time: {now}")]

    else:
        # If an unknown tool name is requested, raise an error.
        # The MCP library will convert this into a proper error response.
        raise ValueError(f"Unknown tool: {name}")

    # Log the tool response to console (stderr so stdout stays clean for MCP)
    response = [{"type": c.type, "text": c.text} for c in result]
    print("RESPONSE", json.dumps(response, indent=2), file=sys.stderr)
    return result


# ── 4. Main entry-point ────────────────────────────────────────
async def main():
    """Start the server and keep it running until the client disconnects."""

    # `stdio_server()` returns a pair of async streams (read, write)
    # connected to the process's stdin and stdout.
    async with stdio_server() as (read_stream, write_stream):

        # `app.run()` starts the MCP event loop:
        #   • reads incoming JSON-RPC messages from read_stream
        #   • dispatches them to our handlers above
        #   • writes responses to write_stream
        # `initialization_options` can carry server-specific config;
        # we pass None to use the defaults.
        await app.run(read_stream, write_stream, app.create_initialization_options())


# Standard Python entry-point guard — only run when executed directly,
# not when imported as a module.
if __name__ == "__main__":
    asyncio.run(main())   # Run the async main() on the default event loop
