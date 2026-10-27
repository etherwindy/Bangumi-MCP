"""MCP resources exposing Bangumi data without a tool call."""

from __future__ import annotations

from typing import Annotated

import mcp.types as types
from mcp.server.mcpserver import MCPServer
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import CalendarOutput, Character, PersonDetail, Subject, User
from bangumi_mcp.tools import ensure_ok, fetch_user

ANNOTATIONS = types.Annotations(audience=["user", "assistant"], priority=0.6)


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.resource(
        "bangumi://calendar",
        name="bangumi_calendar",
        title="Bangumi weekly calendar",
        description="Currently airing anime grouped by weekday.",
        mime_type="application/json",
        annotations=ANNOTATIONS,
    )
    async def calendar_resource() -> CalendarOutput:
        status, payload = await client.get_calendar()
        ensure_ok(status, payload)
        return CalendarOutput.model_validate({"calendar": payload})

    @mcp.resource(
        "bangumi://subject/{subject_id}",
        name="bangumi_subject",
        title="Bangumi subject",
        description="A Bangumi subject (anime, manga, book, music, game or live-action) by id.",
        mime_type="application/json",
        annotations=ANNOTATIONS,
    )
    async def subject_resource(
        subject_id: Annotated[int, Field(ge=1, description="Bangumi subject id")],
    ) -> Subject:
        status, payload = await client.get_subject_info(subject_id)
        return Subject.model_validate(ensure_ok(status, payload))

    @mcp.resource(
        "bangumi://character/{character_id}",
        name="bangumi_character",
        title="Bangumi character",
        description="A Bangumi character by id.",
        mime_type="application/json",
        annotations=ANNOTATIONS,
    )
    async def character_resource(
        character_id: Annotated[int, Field(ge=1, description="Bangumi character id")],
    ) -> Character:
        status, payload = await client.get_character_info(character_id)
        return Character.model_validate(ensure_ok(status, payload))

    @mcp.resource(
        "bangumi://person/{person_id}",
        name="bangumi_person",
        title="Bangumi person",
        description="A Bangumi person (staff, voice actor, author) by id.",
        mime_type="application/json",
        annotations=ANNOTATIONS,
    )
    async def person_resource(
        person_id: Annotated[int, Field(ge=1, description="Bangumi person id")],
    ) -> PersonDetail:
        status, payload = await client.get_person_info(person_id)
        return PersonDetail.model_validate(ensure_ok(status, payload))

    @mcp.resource(
        "bangumi://user/{username}",
        name="bangumi_user",
        title="Bangumi user",
        description="A Bangumi user profile by username.",
        mime_type="application/json",
        annotations=ANNOTATIONS,
    )
    async def user_resource(
        username: Annotated[str, Field(description="Bangumi username")],
    ) -> User:
        return await fetch_user(client, username)
