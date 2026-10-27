"""Shared pytest fixtures."""

from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from bangumi_mcp.bangumi_client import BangumiClient


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def make_client(handler: Callable[[httpx.Request], httpx.Response]) -> BangumiClient:
    """Build a Bangumi client backed by an in-memory HTTP transport."""
    return BangumiClient(
        token="test-token",
        transport=httpx.MockTransport(handler),
        retries=0,
    )


def json_body(request: httpx.Request) -> dict:
    return json.loads(request.content or b"{}")


def make_server(handler: Callable[[httpx.Request], httpx.Response]):
    from bangumi_mcp.mcp_server import create_server

    client = make_client(handler)
    return client, create_server(client)
