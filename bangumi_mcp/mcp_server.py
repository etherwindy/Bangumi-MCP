"""MCP server factory and transport entry points for Bangumi-MCP.

The server is built on :class:`mcp.server.MCPServer` (the class formerly known
as ``FastMCP``). Tool input and output schemas are derived from the Python
type hints and the models in :mod:`bangumi_mcp.models`.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from mcp.server import MCPServer
from mcp.server.caching import CacheHint

from bangumi_mcp import __version__
from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.prompts import register as register_prompts
from bangumi_mcp.resources import register as register_resources
from bangumi_mcp.tools import register_all

SERVER_INSTRUCTIONS = (
    "Bangumi is a Chinese anime/manga/game database. Use `bangumi_search` to "
    "find subjects, characters and staff; `bangumi_get_subject` for a subject "
    "(optionally with characters, staff, relations and episodes); "
    "`bangumi_get_episodes` for episode lists; `bangumi_get_entity` for "
    "characters and real people; `bangumi_get_calendar` for the weekly anime "
    "schedule. Collection tools read or update the authenticated user's "
    "collections and need BANGUMI_API_TOKEN with the matching write scope."
)


def create_server(client: BangumiClient | None = None) -> MCPServer:
    """Create a fully registered Bangumi MCP server.

    Args:
        client: Optional client, mainly for tests. When omitted a client is
            created from the environment and closed when the server stops.
    """
    owns_client = client is None
    client = client or BangumiClient()

    @asynccontextmanager
    async def lifespan(_: MCPServer) -> AsyncIterator[Any]:
        try:
            yield client
        finally:
            if owns_client:
                await client.close()

    mcp = MCPServer(
        name="Bangumi-MCP",
        title="Bangumi",
        description="Search and read Bangumi (bgm.tv) subjects, episodes, characters, persons, indices and collections.",
        instructions=SERVER_INSTRUCTIONS,
        website_url="https://github.com/etherwindy/Bangumi-MCP",
        version=__version__,
        lifespan=lifespan,
        cache_hints={
            "tools/list": CacheHint(ttl_ms=3_600_000, scope="public"),
            "resources/read": CacheHint(ttl_ms=300_000, scope="public"),
            "resources/templates/list": CacheHint(ttl_ms=3_600_000, scope="public"),
            "server/discover": CacheHint(ttl_ms=3_600_000, scope="public"),
        },
    )
    register_all(mcp, client)
    register_resources(mcp, client)
    register_prompts(mcp)
    return mcp


#: Default server used by the CLI transports.
server = create_server()


async def stdio() -> None:
    """Serve the MCP server over stdio."""
    await server.run_stdio_async()


def sse(host: str = "localhost", port: int = 18080) -> None:
    """Serve the legacy HTTP+SSE transport (2025-era clients)."""
    server.run("sse", host=host, port=port)


def streamableHTTP(
    host: str = "localhost",
    port: int = 18080,
    *,
    stateless: bool = False,
    json_response: bool = False,
) -> None:
    """Serve the Streamable HTTP transport."""
    server.run(
        "streamable-http",
        host=host,
        port=port,
        stateless_http=stateless,
        json_response=json_response,
    )


__all__ = ["create_server", "server", "stdio", "sse", "streamableHTTP"]
