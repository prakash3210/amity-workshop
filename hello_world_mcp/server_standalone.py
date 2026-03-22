# ============================================================
# server_standalone.py — Hello World MCP Server (HTTP)
# Run this first. It starts the same MCP server as server.py but
# over Streamable HTTP on port 8000, so a separate client can
# connect without spawning this process.
#
# Usage:
#   Terminal 1: python server_standalone.py
#   Terminal 2: python clientstandalone.py
# ============================================================

import contextlib
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

from server import app as mcp_app
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager


class StreamableHTTPASGIApp:
    """ASGI app that delegates to the session manager."""

    def __init__(self, session_manager: StreamableHTTPSessionManager):
        self.session_manager = session_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.session_manager.handle_request(scope, receive, send)


def create_starlette_app() -> Starlette:
    """Build Starlette app with MCP at /mcp."""
    session_manager = StreamableHTTPSessionManager(
        mcp_app,
        json_response=True,
    )
    mcp_asgi = StreamableHTTPASGIApp(session_manager)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with session_manager.run():
            yield

    return Starlette(
        routes=[Mount("/mcp", app=mcp_asgi)],
        lifespan=lifespan,
    )


if __name__ == "__main__":
    starlette_app = create_starlette_app()
    uvicorn.run(starlette_app, host="127.0.0.1", port=8000, log_level="info")
