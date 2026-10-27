"""Revision history tool."""

from __future__ import annotations

from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import Revision, RevisionsResult

from . import READ_ONLY, ensure_ok

RevisionEntity = Literal["subject", "episode", "character", "person"]


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_get_revisions",
        title="Get Bangumi revision history",
        description=(
            "Read the wiki revision history for a subject, episode, character "
            "or person. Pass `entity_id` to list revisions (newest first) or "
            "`revision_id` to get one revision's full diff payload."
        ),
        annotations=READ_ONLY,
    )
    async def get_revisions(
        entity: Annotated[
            RevisionEntity, Field(description="Which entity type the revision belongs to")
        ],
        entity_id: Annotated[
            int | None,
            Field(ge=1, description="Subject/episode/character/person id: list its revisions"),
        ] = None,
        revision_id: Annotated[
            int | None, Field(ge=1, description="Revision id: fetch one revision")
        ] = None,
        limit: Annotated[int, Field(ge=1, le=50, description="Page size (max 50)")] = 30,
        offset: Annotated[int, Field(ge=0, description="Pagination offset")] = 0,
    ) -> RevisionsResult:
        if (entity_id is None) == (revision_id is None):
            raise ToolError("Provide exactly one of entity_id or revision_id")

        listers = {
            "subject": client.get_subject_revisions,
            "episode": client.get_episode_revisions,
            "character": client.get_character_revisions,
            "person": client.get_person_revisions,
        }
        detailers = {
            "subject": client.get_subject_revision_info,
            "episode": client.get_episode_revision_info,
            "character": client.get_character_revision_info,
            "person": client.get_person_revision_info,
        }

        if revision_id is not None:
            status, payload = await detailers[entity](revision_id)
            ensure_ok(status, payload)
            return RevisionsResult(entity=entity, revision=payload)

        key = f"{entity}_id"
        status, payload = await listers[entity](
            {key: entity_id, "limit": limit, "offset": offset}
        )
        ensure_ok(status, payload)
        return RevisionsResult(
            entity=entity,
            total=payload.get("total"),
            limit=payload.get("limit"),
            offset=payload.get("offset"),
            data=[Revision.model_validate(item) for item in payload.get("data", [])],
        )
