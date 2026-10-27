"""Episode tools."""

from __future__ import annotations

from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import Episode, EpisodeDetail, EpisodeResult

from . import READ_ONLY, ensure_ok

EpisodeType = Literal[0, 1, 2, 3, 4, 5, 6]


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_get_episodes",
        title="Get Bangumi episodes",
        description=(
            "Get episodes of a subject (`subject_id`) or the details of one "
            "episode (`episode_id`). Exactly one of the two ids is required. "
            "Episode list entries include air date, duration, sort number and "
            "comment count."
        ),
        annotations=READ_ONLY,
    )
    async def get_episodes(
        subject_id: Annotated[
            int | None, Field(ge=1, description="Subject id: list its episodes")
        ] = None,
        episode_id: Annotated[
            int | None, Field(ge=1, description="Episode id: get one episode")
        ] = None,
        episode_type: Annotated[
            EpisodeType | None,
            Field(
                description=(
                    "With subject_id: 0 main, 1 special, 2 OP, 3 ED, 4 PV, "
                    "5 MAD, 6 other; omit for all types"
                )
            ),
        ] = None,
        limit: Annotated[int, Field(ge=1, le=200, description="Page size (max 200)")] = 100,
        offset: Annotated[int, Field(ge=0, description="Pagination offset")] = 0,
    ) -> EpisodeResult:
        if (subject_id is None) == (episode_id is None):
            raise ToolError("Provide exactly one of subject_id or episode_id")

        if episode_id is not None:
            status, payload = await client.get_episode_info(episode_id)
            ensure_ok(status, payload)
            return EpisodeResult(episode=EpisodeDetail.model_validate(payload))

        params: dict[str, object] = {
            "subject_id": subject_id,
            "limit": limit,
            "offset": offset,
        }
        if episode_type is not None:
            params["type"] = episode_type
        status, payload = await client.get_episodes(params)
        ensure_ok(status, payload)
        return EpisodeResult.model_validate(payload)
