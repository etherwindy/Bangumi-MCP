"""MCP server wiring for Bangumi-MCP.

The project runs on the MCP Python SDK 2.x. The low-level ``Server`` is used
here because the tool catalogue is generated from the Bangumi OpenAPI document
and therefore needs full control over input/output JSON Schemas.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import mcp.types as types
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from . import tools
from .tool_list import tool_list

logger = logging.getLogger(__name__)

SERVER_INSTRUCTIONS = (
    "Bangumi-MCP exposes Bangumi API tools for searching and reading subjects, "
    "episodes, characters, persons, indices, revisions, users, and collections. "
    "Tools that modify authenticated user data are annotated as mutating and "
    "require a Bangumi API token with the matching write scope."
)


def _is_content_list(result: Any) -> bool:
    if not isinstance(result, list):
        return False
    content_types = (
        types.TextContent,
        types.ImageContent,
        types.AudioContent,
        types.ResourceLink,
        types.EmbeddedResource,
    )
    return all(isinstance(item, content_types) for item in result)


def _to_call_tool_result(result: Any, is_error: bool = False) -> types.CallToolResult:
    if isinstance(result, types.CallToolResult):
        return result

    if _is_content_list(result):
        text_errors = [
            item.text
            for item in result
            if isinstance(item, types.TextContent) and item.text.startswith("Error:")
        ]
        return types.CallToolResult(
            content=result, is_error=is_error or bool(text_errors)
        )

    if isinstance(result, dict):
        is_api_error = "title" in result and (
            "description" in result or "details" in result or "request_id" in result
        )
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2),
                )
            ],
            structured_content=result,
            is_error=is_error or is_api_error,
        )

    text = json.dumps(result, ensure_ascii=False, indent=2)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        is_error=is_error,
    )


async def _handle_list_tools(
    ctx: Any, params: Optional[types.PaginatedRequestParams]
) -> types.ListToolsResult:
    """Return the complete tool catalogue (no pagination needed)."""
    return types.ListToolsResult(tools=tool_list)


async def _handle_call_tool(
    ctx: Any, params: types.CallToolRequestParams
) -> types.CallToolResult:
    """Dispatch a tool call to the matching function in ``tools``."""
    name = params.name
    arguments: Dict[str, Any] = params.arguments or {}
    try:
        tool = getattr(tools, name, None)
        if tool is None:
            return _to_call_tool_result(
                [types.TextContent(type="text", text=f"Unknown tool: {name}")],
                is_error=True,
            )
        result = await tool(arguments)
        return _to_call_tool_result(result)
    except Exception as exc:  # noqa: BLE001 - surface the message to the model
        logger.exception("Error in tool %s", name)
        return _to_call_tool_result(
            [types.TextContent(type="text", text=f"Error: {exc}")],
            is_error=True,
        )


# Handlers are passed to the constructor in MCP SDK 2.x; the decorator form of
# v1 is gone. The server still speaks both protocol eras.
server = Server(
    "Bangumi-MCP",
    version="0.2.0",
    instructions=SERVER_INSTRUCTIONS,
    on_list_tools=_handle_list_tools,
    on_call_tool=_handle_call_tool,
)


async def stdio() -> None:
    """Serve the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


def sse(host: str = "localhost", port: int = 18080) -> None:
    """Serve the legacy HTTP+SSE transport (for 2025-era clients)."""
    transport = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with transport.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):
            await server.run(
                read_stream, write_stream, server.create_initialization_options()
            )

    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages", app=transport.handle_post_message),
        ],
    )
    uvicorn.run(starlette_app, host=host, port=port)


def streamableHTTP(
    host: str = "localhost",
    port: int = 18080,
    *,
    stateless: bool = False,
    json_response: bool = False,
) -> None:
    """Serve the Streamable HTTP transport (current MCP transports)."""
    starlette_app = server.streamable_http_app(
        streamable_http_path="/mcp",
        json_response=json_response,
        stateless_http=stateless,
        host=host,
    )
    uvicorn.run(starlette_app, host=host, port=port)
