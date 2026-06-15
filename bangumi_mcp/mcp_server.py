"""MCP server for Bangumi API."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.streamable_http import StreamableHTTPServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send
from collections.abc import AsyncIterator
import contextlib
import uvicorn

from .tool_list import tool_list  # Import tool list from tool_list.py
from . import tools  # Import all tools from tools.py

# Set up logging
logger = logging.getLogger(__name__)

SERVER_INSTRUCTIONS = (
    "Bangumi-MCP exposes Bangumi API tools for searching and reading subjects, "
    "episodes, characters, persons, indices, revisions, users, and collections. "
    "Tools that modify authenticated user data are annotated as mutating."
)

# Create server instance
server = Server("Bangumi-MCP", version="0.1.0", instructions=SERVER_INSTRUCTIONS)


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
            item.text for item in result
            if isinstance(item, types.TextContent) and item.text.startswith("Error:")
        ]
        return types.CallToolResult(content=result, isError=is_error or bool(text_errors))

    if isinstance(result, dict):
        is_api_error = "title" in result and (
            "description" in result or "details" in result or "request_id" in result
        )
        return types.CallToolResult(
            content=[types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )],
            structuredContent=result,
            isError=is_error or is_api_error,
        )

    text = json.dumps(result, ensure_ascii=False, indent=2)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        isError=is_error,
    )

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    Handle tool listing.
    Returns:
        List of available tools.
    """
    return tool_list


@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> types.CallToolResult:
    """
    Handle tool calls.
    Args:
        name: The name of the tool to call.
        arguments: Arguments for the tool.
    Returns:
        List of TextContent with the tool's output.
    Raises:
        Exception: If the tool does not exist or an error occurs.
    """

    try:
        if hasattr(tools, name):
            tool = getattr(tools, name)
            # 如果工具是异步函数，使用 await 调用
            if asyncio.iscoroutinefunction(tool):
                return _to_call_tool_result(await tool(arguments))
            else:
                return _to_call_tool_result(
                    [types.TextContent(type="text", text="Error: Tool function is not async")],
                    is_error=True,
                )
        else:
            return _to_call_tool_result(
                [types.TextContent(type="text", text=f"Unknown tool: {name}")],
                is_error=True,
            )
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return _to_call_tool_result(
            [types.TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True,
        )


async def stdio():
    """
    Main entry point for the MCP server using stdio transport.
    Initializes the Bangumi client and starts the server.
    This is useful for testing or running in environments where standard input/output is available.
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def sse(host: str = 'localhost', port: int = 18080):
    """
    Main entry point for the MCP server using SSE transport.
    Initializes the Bangumi client and starts the server.
    Args:
        host: Host to bind to.
        port: Port to listen on.
    """
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages", app=sse.handle_post_message),
        ],
    )
    uvicorn.run(starlette_app, host=host, port=port)


def streamableHTTP(host: str = 'localhost', port: int = 18080):
    """
    Main entry point for the MCP server using Streamable HTTP transport.
    Initializes the Bangumi client and starts the server.
    Args:
        host: Host to bind to.
        port: Port to listen on.
    """
    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=None,
        json_response=False,
        stateless=False
    )

    async def handle_streamable_http(
            scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            
            finally:
                print("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=False,
        routes=[
            Mount("/mcp/", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # 3) Launch via Uvicorn
    uvicorn.run(starlette_app, host=host, port=port)
