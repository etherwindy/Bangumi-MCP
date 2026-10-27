"""Character and person detail tool."""

from __future__ import annotations

import asyncio
from typing import Annotated, Literal

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import (
    Character,
    CharacterPerson,
    EntityDetail,
    PersonCharacter,
    PersonDetail,
    SubjectRelation,
)

from . import READ_ONLY, ensure_ok

Entity = Literal["character", "person"]
IncludeKind = Literal["subjects", "characters", "persons"]


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_get_entity",
        title="Get Bangumi character or person",
        description=(
            "Get a character or a real person (staff, voice actor, author) by "
            "id. Pass `include` to also fetch the subjects they appear in and "
            "the persons/characters they are linked to. Character ids come from "
            "`bangumi_get_subject` or `bangumi_search`."
        ),
        annotations=READ_ONLY,
    )
    async def get_entity(
        ctx: Context,
        entity: Annotated[
            Entity, Field(description="character = fictional character, person = real person/staff")
        ],
        entity_id: Annotated[int, Field(ge=1, description="Character or person id")],
        include: Annotated[
            list[IncludeKind] | None,
            Field(
                description=(
                    "Extra sections: subjects (works they appear in); persons "
                    "(character only: staff/voice actors); characters (person "
                    "only: characters they are linked to)"
                )
            ),
        ] = None,
    ) -> EntityDetail:
        include_set = set(include or [])
        if entity == "character":
            invalid = include_set - {"subjects", "persons"}
            if invalid:
                raise ToolError(
                    f"Unsupported include for character: {sorted(invalid)}; use subjects/persons"
                )
            status, payload = await client.get_character_info(entity_id)
            detail = EntityDetail(
                entity_type="character",
                character=Character.model_validate(ensure_ok(status, payload)),
            )

            async def load_subjects() -> list[SubjectRelation]:
                code, data = await client.get_character_subjects(entity_id)
                return [SubjectRelation.model_validate(item) for item in ensure_ok(code, data)]

            async def load_persons() -> list[CharacterPerson]:
                code, data = await client.get_character_persons(entity_id)
                return [CharacterPerson.model_validate(item) for item in ensure_ok(code, data)]

            tasks: list[tuple[str, object]] = []
            if "subjects" in include_set:
                tasks.append(("subjects", load_subjects))
            if "persons" in include_set:
                tasks.append(("related_persons", load_persons))
        else:
            invalid = include_set - {"subjects", "characters"}
            if invalid:
                raise ToolError(
                    f"Unsupported include for person: {sorted(invalid)}; use subjects/characters"
                )
            status, payload = await client.get_person_info(entity_id)
            detail = EntityDetail(
                entity_type="person",
                person=PersonDetail.model_validate(ensure_ok(status, payload)),
            )

            async def load_subjects_person() -> list[SubjectRelation]:
                code, data = await client.get_person_subjects(entity_id)
                return [SubjectRelation.model_validate(item) for item in ensure_ok(code, data)]

            async def load_characters() -> list[PersonCharacter]:
                code, data = await client.get_person_characters(entity_id)
                return [PersonCharacter.model_validate(item) for item in ensure_ok(code, data)]

            tasks = []
            if "subjects" in include_set:
                tasks.append(("subjects", load_subjects_person))
            if "characters" in include_set:
                tasks.append(("related_characters", load_characters))

        if tasks:
            await ctx.report_progress(0, len(tasks), "Loading related sections")
            results = await asyncio.gather(*(loader() for _, loader in tasks))
            for (name, _), result in zip(tasks, results):
                setattr(detail, name, result)
            await ctx.report_progress(len(tasks), len(tasks), "Done")
        return detail
