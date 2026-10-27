"""Tool registration for the Bangumi MCP server.

Each module exposes ``register(mcp, client)`` and registers the subset of
Bangumi tools it owns. The tools are grouped by user intent rather than by
REST endpoint so the model sees a small, non-overlapping catalogue.
"""

from __future__ import annotations

from typing import Any, NoReturn

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import User

READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)
WRITE = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)
DESTRUCTIVE = ToolAnnotations(
    read_only_hint=False, destructive_hint=True, idempotent_hint=True, open_world_hint=True
)


def fail(status_code: int, payload: Any) -> NoReturn:
    """Raise a readable ``ToolError`` for a failed Bangumi API response."""
    data = payload if isinstance(payload, dict) else {}
    title = data.get("title") or "request failed"
    description = data.get("description") or ""
    hint = data.get("hint") or ""
    details = data.get("details")
    if not description and isinstance(details, str):
        description = details
    message = f"Bangumi API error {status_code}: {title}"
    if description:
        message += f" ({description})"
    if hint:
        message += f" Hint: {hint}"
    raise ToolError(message)


def ensure_ok(status_code: int, payload: Any) -> Any:
    """Return the payload for a 2xx response, otherwise raise ``ToolError``."""
    if status_code >= 400:
        fail(status_code, payload)
    return payload


async def fetch_user(client: BangumiClient, username: str | None) -> User:
    """Return a user profile, resolving ``/v0/me`` when no name is given."""
    if username:
        status, payload = await client.get_user_info(username)
    else:
        status, payload = await client.get_me_info()
    return User.model_validate(ensure_ok(status, payload))


def register_all(mcp: MCPServer, client: BangumiClient) -> None:
    """Register every tool group on ``mcp``."""
    from . import calendar, collections, entities, episodes, indices, revisions, search, subjects, users

    for module in (
        calendar,
        search,
        subjects,
        episodes,
        entities,
        revisions,
        users,
        collections,
        indices,
    ):
        module.register(mcp, client)


__all__ = ["READ_ONLY", "WRITE", "DESTRUCTIVE", "ensure_ok", "fail", "fetch_user", "register_all"]
