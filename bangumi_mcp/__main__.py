#!/usr/bin/env python3
"""Entry point for the Bangumi MCP server when run as a module."""

import asyncio
import argparse
from .mcp_server import sse
from .mcp_server import stdio
from .mcp_server import streamableHTTP

def main():
    """Main entry point for the Bangumi MCP server."""
    parser = argparse.ArgumentParser(description='Run MCP server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    parser.add_argument('--mode', choices=['stdio', 'sse', 'streamable_http'], default='stdio', help='Mode to run the server in')
    args = parser.parse_args()
    if args.mode == 'stdio':
        asyncio.run(stdio())
    elif args.mode == 'sse':
        sse(host=args.host, port=args.port)
    elif args.mode == 'streamable_http':
        streamableHTTP(host=args.host, port=args.port)
    else:
        raise ValueError(f"Unknown mode: {args.mode}")

if __name__ == "__main__":
    main()