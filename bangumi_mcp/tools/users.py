"""User profile tool."""

from __future__ import annotations

from typing import Annotated

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import User

from . import READ_ONLY, fetch_user


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_get_user",
        title="Get Bangumi user profile",
        description=(
            "Get a Bangumi user by username (id, nickname, avatar, signature, "
            "user group). Omit the username to get the authenticated user's "
            "own profile; that requires BANGUMI_API_TOKEN."
        ),
        annotations=READ_ONLY,
    )
    async def get_user(
        username: Annotated[
            str | None, Field(description="Bangumi username; omit for the current user")
        ] = None,
    ) -> User:
        return await fetch_user(client, username)
