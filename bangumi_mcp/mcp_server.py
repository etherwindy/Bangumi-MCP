"""MCP server for Bangumi API."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn

from .tool_list import tool_list  # Import tool list from tool_list.py
from . import tools  # Import all tools from tools.py

# Set up logging
logger = logging.getLogger(__name__)

# Create server instance
server = Server("Bangumi-MCP")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    Handle tool listing.
    Returns:
        List of available tools.
    """
    return tool_list


@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
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
            # 如果工具是异步函数，使用 await 调用
            if asyncio.iscoroutinefunction(getattr(tools, name)):
                return await getattr(tools, name)(arguments)
            else:
                return [types.TextContent(
                    type="text",
                    text="Error: Tool function is not async"
                )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
    Create a Starlette application for the MCP server using SSE transport.
    Args:
        mcp_server: The MCP server instance.
        debug: Whether to run the app in debug mode.
    Returns:
        Starlette application instance.
    """
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def sse(host: str = 'localhost', port: int = 18080):
    """
    Main entry point for the MCP server using SSE transport.
    Initializes the Bangumi client and starts the server.
    Args:
        host: Host to bind to.
        port: Port to listen on.
    """
    starlette_app = create_starlette_app(server, debug=True)
    uvicorn.run(starlette_app, host=host, port=port)


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
            InitializationOptions(
                server_name="Bangumi-MCP",
                server_version="0.1.0",
                capabilities=types.ServerCapabilities(
                    tools=types.ToolsCapability(listChanged=False)
                )
            )
        )

