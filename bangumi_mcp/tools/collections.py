"""Collection reading and writing tools."""

from __future__ import annotations

from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import (
    CharacterCollectionsResult,
    CollectionsResult,
    EpisodeCollectionsResult,
    PersonCollectionsResult,
    SubjectCollectionsResult,
    UserCharacterCollection,
    UserEpisodeCollection,
    UserPersonCollection,
    UserSubjectCollection,
    WriteResult,
)

from . import DESTRUCTIVE, READ_ONLY, ensure_ok

SubjectType = Literal[1, 2, 3, 4, 6]
SubjectCollectionType = Literal[1, 2, 3, 4, 5]
EpisodeCollectionType = Literal[0, 1, 2, 3]
EpisodeType = Literal[0, 1, 2, 3, 4, 5, 6]


async def _resolve_username(client: BangumiClient, username: str | None) -> str:
    if username:
        return username
    status, payload = await client.get_me_info()
    body = ensure_ok(status, payload)
    resolved = body.get("username")
    if not resolved:
        raise ToolError(
            "Could not resolve the current Bangumi user. Pass `username`, or "
            "set BANGUMI_API_TOKEN to authenticate."
        )
    return str(resolved)


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_get_collections",
        title="Get Bangumi collections",
        description=(
            "Read Bangumi collections. `resource=subject` lists a user's "
            "subject collections (optionally one subject); `resource=episode` "
            "reads the current user's episode progress; `resource=character` "
            "and `resource=person` list character/person collections. Omit "
            "`username` to read the authenticated user's collections."
        ),
        annotations=READ_ONLY,
    )
    async def get_collections(
        resource: Annotated[
            Literal["subject", "episode", "character", "person"],
            Field(description="Which collection type to read"),
        ] = "subject",
        username: Annotated[
            str | None,
            Field(description="Bangumi username; omit for the authenticated user (requires token)"),
        ] = None,
        subject_id: Annotated[
            int | None,
            Field(description="Subject collection: return only this subject; episode resource: parent subject"),
        ] = None,
        episode_id: Annotated[
            int | None, Field(description="Episode resource: return only this episode")
        ] = None,
        character_id: Annotated[
            int | None, Field(description="Character resource: return only this character")
        ] = None,
        person_id: Annotated[
            int | None, Field(description="Person resource: return only this person")
        ] = None,
        subject_type: Annotated[
            SubjectType | None, Field(description="Subject list: filter by subject type")
        ] = None,
        status: Annotated[
            SubjectCollectionType | None,
            Field(
                description="Subject list: 1 wish, 2 done, 3 doing, 4 on hold, 5 dropped"
            ),
        ] = None,
        episode_type: Annotated[
            EpisodeType | None,
            Field(description="Episode list: filter by episode type (0 main ... 6 other)"),
        ] = None,
        limit: Annotated[int, Field(ge=1, le=1000, description="Page size")] = 30,
        offset: Annotated[int, Field(ge=0, description="Pagination offset")] = 0,
    ) -> CollectionsResult:
        if resource == "subject":
            name = await _resolve_username(client, username)
            if subject_id is not None:
                code, payload = await client.get_user_collection_info(name, subject_id)
                ensure_ok(code, payload)
                return SubjectCollectionsResult(
                    collection=UserSubjectCollection.model_validate(payload)
                )
            params: dict[str, object] = {"limit": limit, "offset": offset}
            if subject_type is not None:
                params["subject_type"] = subject_type
            if status is not None:
                params["type"] = status
            code, payload = await client.get_user_collections(name, params)
            body = ensure_ok(code, payload)
            return SubjectCollectionsResult(
                total=body.get("total"),
                limit=body.get("limit"),
                offset=body.get("offset"),
                data=[UserSubjectCollection.model_validate(item) for item in body.get("data", [])],
            )

        if resource == "episode":
            if episode_id is not None:
                code, payload = await client.get_my_episode_collection_info(episode_id)
                ensure_ok(code, payload)
                return EpisodeCollectionsResult(
                    collection=UserEpisodeCollection.model_validate(payload)
                )
            if subject_id is None:
                raise ToolError("episode resource requires subject_id (list) or episode_id (single)")
            params = {"limit": limit, "offset": offset}
            if episode_type is not None:
                params["episode_type"] = episode_type
            code, payload = await client.get_my_episode_collections(subject_id, params)
            body = ensure_ok(code, payload)
            return EpisodeCollectionsResult(
                total=body.get("total"),
                limit=body.get("limit"),
                offset=body.get("offset"),
                data=[UserEpisodeCollection.model_validate(item) for item in body.get("data", [])],
            )

        name = await _resolve_username(client, username)
        if resource == "character":
            if character_id is not None:
                code, payload = await client.get_user_character_collection_info(name, character_id)
                ensure_ok(code, payload)
                return CharacterCollectionsResult(
                    collection=UserCharacterCollection.model_validate(payload)
                )
            code, payload = await client.get_user_character_collections(name)
            body = ensure_ok(code, payload)
            return CharacterCollectionsResult(
                total=body.get("total"),
                limit=body.get("limit"),
                offset=body.get("offset"),
                data=[UserCharacterCollection.model_validate(item) for item in body.get("data", [])],
            )

        if person_id is not None:
            code, payload = await client.get_user_person_collection_info(name, person_id)
            ensure_ok(code, payload)
            return PersonCollectionsResult(
                collection=UserPersonCollection.model_validate(payload)
            )
        code, payload = await client.get_user_person_collections(name)
        body = ensure_ok(code, payload)
        return PersonCollectionsResult(
            total=body.get("total"),
            limit=body.get("limit"),
            offset=body.get("offset"),
            data=[UserPersonCollection.model_validate(item) for item in body.get("data", [])],
        )

    @mcp.tool(
        name="bangumi_update_collection",
        title="Update Bangumi collections",
        description=(
            "Write collection state for the authenticated user. "
            "`resource=subject`: set/update a subject collection (status, rating, "
            "comment, privacy, tags, book progress); `resource=episode`: mark "
            "episodes watched/wish/dropped, one or many at once; "
            "`resource=character|person|index` with `action=set|unset`: collect "
            "or uncollect. Requires BANGUMI_API_TOKEN with write:collection "
            "(or write:indices for indices). Known gap: Bangumi's API does not "
            "implement uncollecting characters or persons yet."
        ),
        annotations=DESTRUCTIVE,
    )
    async def update_collection(
        resource: Annotated[
            Literal["subject", "episode", "character", "person", "index"],
            Field(description="What to collect or update"),
        ],
        action: Annotated[
            Literal["set", "unset"],
            Field(description="set = collect/update, unset = uncollect (character/person/index only)"),
        ] = "set",
        subject_id: Annotated[
            int | None, Field(description="Subject resource: subject id; episode resource: parent subject id")
        ] = None,
        episode_id: Annotated[
            int | None, Field(description="Episode resource: one episode id (single update)")
        ] = None,
        episode_ids: Annotated[
            list[int] | None,
            Field(description="Episode resource: batch of episode ids (requires subject_id)"),
        ] = None,
        character_id: Annotated[int | None, Field(description="Character resource: character id")] = None,
        person_id: Annotated[int | None, Field(description="Person resource: person id")] = None,
        index_id: Annotated[int | None, Field(description="Index resource: index id")] = None,
        status: Annotated[
            int | None,
            Field(
                description=(
                    "subject: 1 wish, 2 done, 3 doing, 4 on hold, 5 dropped; "
                    "episode: 0 none, 1 wish, 2 done, 3 dropped"
                )
            ),
        ] = None,
        rating: Annotated[
            int | None, Field(ge=0, le=10, description="Subject rating 0-10 (0 removes the rating)")
        ] = None,
        comment: Annotated[str | None, Field(description="Subject comment")] = None,
        private: Annotated[bool | None, Field(description="Subject only: hide from others")] = None,
        tags: Annotated[
            list[str] | None, Field(description="Subject only: replace tags; [] clears them")
        ] = None,
        ep_status: Annotated[
            int | None, Field(ge=0, description="Books only: watched/read episode count")
        ] = None,
        vol_status: Annotated[
            int | None, Field(ge=0, description="Books only: read volume count")
        ] = None,
    ) -> WriteResult:
        if resource == "subject":
            if action != "set":
                raise ToolError("A subject collection cannot be unset; use status=... instead")
            if subject_id is None:
                raise ToolError("subject resource requires subject_id")
            payload: dict[str, object] = {
                key: value
                for key, value in {
                    "type": status,
                    "rate": rating,
                    "comment": comment,
                    "private": private,
                    "tags": tags,
                    "ep_status": ep_status,
                    "vol_status": vol_status,
                }.items()
                if value is not None
            }
            if not payload:
                raise ToolError("Provide at least one of status/rating/comment/private/tags/ep_status/vol_status")
            if status is not None and status not in (1, 2, 3, 4, 5):
                raise ToolError("subject status must be 1-5")
            code, result = await client.post_my_collection(subject_id, payload)
            ensure_ok(code, result)
            return WriteResult(
                resource="subject",
                action="update",
                ids=[subject_id],
                message=f"Subject {subject_id} collection updated.",
            )

        if resource == "episode":
            if action != "set":
                raise ToolError("An episode collection cannot be unset; use status=0 instead")
            if status is None or status not in (0, 1, 2, 3):
                raise ToolError("episode updates require status 0-3")
            if subject_id is not None:
                ids = list(episode_ids or ([episode_id] if episode_id else []))
                if not ids:
                    raise ToolError("Provide episode_ids (or episode_id) together with subject_id")
                code, result = await client.patch_my_episode_collections(
                    subject_id, {"episode_id": ids, "type": status}
                )
                ensure_ok(code, result)
                return WriteResult(
                    resource="episode",
                    action="update",
                    ids=ids,
                    message=f"Episodes {ids} marked with status {status}.",
                )
            if episode_id is None:
                raise ToolError("episode resource requires episode_id, or subject_id + episode_ids")
            code, result = await client.put_my_episode_collection_info(
                episode_id, {"type": status}
            )
            ensure_ok(code, result)
            return WriteResult(
                resource="episode",
                action="update",
                ids=[episode_id],
                message=f"Episode {episode_id} marked with status {status}.",
            )

        id_map = {
            "character": (character_id, client.post_character_collection, client.delete_character_collection),
            "person": (person_id, client.post_person_collection, client.delete_person_collection),
            "index": (index_id, client.post_index_collection, client.delete_index_collection),
        }
        entity_id, collect, uncollect = id_map[resource]
        if entity_id is None:
            raise ToolError(f"{resource} resource requires {resource}_id")
        code, result = await (collect(entity_id) if action == "set" else uncollect(entity_id))
        if code == 404 and action == "unset" and resource in ("character", "person"):
            # bangumi/server comments out these DELETE routes; the OpenAPI
            # document still advertises them. See bangumi/api#234.
            raise ToolError(
                f"Bangumi's public API does not implement uncollecting {resource}s yet "
                f"(upstream bangumi/api#234). Remove the {resource} collection on "
                "https://bgm.tv instead."
            )
        ensure_ok(code, result)
        verb = "collected" if action == "set" else "uncollected"
        return WriteResult(
            resource=resource,
            action=action,
            ids=[entity_id],
            message=f"{resource.capitalize()} {entity_id} {verb}.",
        )
