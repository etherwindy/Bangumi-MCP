#!/usr/bin/env python3
"""Entry point for the Bangumi MCP server when run as a module."""

from __future__ import annotations

import argparse
import asyncio

from bangumi_mcp import __version__
from bangumi_mcp.mcp_server import sse, stdio, streamableHTTP


def main() -> None:
    """Run the MCP server with the selected transport."""
    parser = argparse.ArgumentParser(
        prog="bangumi-mcp",
        description="Bangumi MCP server (MCP SDK 2.x)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse", "streamable_http"],
        default="stdio",
        help="Transport to serve (default: stdio)",
    )
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=18080, help="Port to listen on")
    parser.add_argument(
        "--stateless",
        action="store_true",
        help="Disable Streamable HTTP sessions (stateful by default)",
    )
    parser.add_argument(
        "--json-response",
        action="store_true",
        help="Return JSON responses instead of SSE streams over Streamable HTTP",
    )
    args = parser.parse_args()

    if args.mode == "stdio":
        asyncio.run(stdio())
    elif args.mode == "sse":
        sse(host=args.host, port=args.port)
    else:
        streamableHTTP(
            host=args.host,
            port=args.port,
            stateless=args.stateless,
            json_response=args.json_response,
        )


if __name__ == "__main__":
    main()
