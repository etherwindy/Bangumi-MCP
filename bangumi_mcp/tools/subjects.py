"""Subject detail tool."""

from __future__ import annotations

import asyncio
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import (
    Episode,
    RelatedCharacter,
    RelatedPerson,
    Subject,
    SubjectDetail,
    SubjectRelation,
)

from . import READ_ONLY, ensure_ok

IncludeKind = Literal["characters", "persons", "relations", "episodes"]
EpisodeType = Literal[0, 1, 2, 3, 4, 5, 6]


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_get_subject",
        title="Get Bangumi subject details",
        description=(
            "Get a subject (anime, manga, book, music, game or live-action) by "
            "id: summary, infobox, rating, tags, cover images and collection "
            "counts are always included. Pass `include` to fetch related "
            "characters, staff, related subjects or the episode list in the "
            "same call. Prefer this over several narrow calls."
        ),
        annotations=READ_ONLY,
    )
    async def get_subject(
        subject_id: Annotated[int, Field(ge=1, description="Bangumi subject id")],
        include: Annotated[
            list[IncludeKind] | None,
            Field(
                description=(
                    "Extra sections to fetch: characters, persons (staff), "
                    "relations (sequels/spin-offs/etc.) and episodes"
                )
            ),
        ] = None,
        episode_type: Annotated[
            EpisodeType | None,
            Field(
                description=(
                    "Only with include=episodes: 0 main, 1 special, 2 OP, 3 ED, "
                    "4 PV, 5 MAD, 6 other; omit for all types"
                )
            ),
        ] = None,
        episode_limit: Annotated[
            int, Field(ge=1, le=200, description="Only with include=episodes: max episodes to return")
        ] = 100,
    ) -> SubjectDetail:
        include_set = set(include or [])

        status, payload = await client.get_subject_info(subject_id)
        detail = SubjectDetail(subject=Subject.model_validate(ensure_ok(status, payload)))

        async def load_characters() -> list[RelatedCharacter]:
            code, data = await client.get_subject_characters(subject_id)
            return [RelatedCharacter.model_validate(item) for item in ensure_ok(code, data)]

        async def load_persons() -> list[RelatedPerson]:
            code, data = await client.get_subject_persons(subject_id)
            return [RelatedPerson.model_validate(item) for item in ensure_ok(code, data)]

        async def load_relations() -> list[SubjectRelation]:
            code, data = await client.get_subject_relations(subject_id)
            return [SubjectRelation.model_validate(item) for item in ensure_ok(code, data)]

        async def load_episodes() -> list[Episode]:
            params: dict[str, object] = {
                "subject_id": subject_id,
                "limit": episode_limit,
                "offset": 0,
            }
            if episode_type is not None:
                params["type"] = episode_type
            code, data = await client.get_episodes(params)
            body = ensure_ok(code, data)
            return [Episode.model_validate(item) for item in body.get("data", [])]

        loads = {
            "characters": load_characters,
            "persons": load_persons,
            "relations": load_relations,
            "episodes": load_episodes,
        }
        requested = [(name, loads[name]) for name in loads if name in include_set]
        if requested:
            results = await asyncio.gather(*(loader() for _, loader in requested))
            for (name, _), result in zip(requested, results):
                setattr(detail, name, result)

        return detail
