#!/usr/bin/env python3
"""Entry point for the Bangumi MCP server."""

import asyncio
import argparse
from bangumi_mcp.mcp_server import sse
from bangumi_mcp.mcp_server import stdio

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    args = parser.parse_args()
    sse(host=args.host, port=args.port)
