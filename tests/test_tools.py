"""End-to-end tests for the consolidated tool catalogue."""

from __future__ import annotations

import json
import httpx
import pytest
from mcp import Client

from conftest import json_body, make_server

SUBJECT = {
    "id": 237,
    "type": 2,
    "name": "GHOST IN THE SHELL / 攻殻機動隊",
    "name_cn": "攻壳机动队",
    "summary": "2029 年，公安九课。",
    "nsfw": False,
    "locked": False,
    "platform": "剧场版",
    "meta_tags": [],
    "volumes": 0,
    "eps": 1,
    "series": False,
    "total_episodes": 1,
    "date": "1995-11-18",
    "images": {
        "large": "https://example.invalid/l.jpg",
        "common": "https://example.invalid/c.jpg",
        "medium": "https://example.invalid/m.jpg",
        "small": "https://example.invalid/s.jpg",
        "grid": "https://example.invalid/g.jpg",
    },
    "rating": {"rank": 10, "total": 100, "count": {"10": 50}, "score": 8.9},
    "collection": {"wish": 1, "collect": 2, "doing": 3, "on_hold": 4, "dropped": 5},
    "tags": [{"name": "科幻", "count": 10, "total_count": 20}],
}

EPISODE = {
    "id": 96821,
    "type": 0,
    "name": "GHOST IN THE SHELL",
    "name_cn": "",
    "sort": 1,
    "ep": 1,
    "airdate": "1995-11-18",
    "comment": 30,
    "duration": "00:83:00",
    "desc": "",
    "disc": 0,
    "subject_id": 237,
}

RELATED_CHARACTER = {
    "id": 1,
    "name": "草薙素子",
    "summary": "",
    "type": 1,
    "relation": "主角",
    "images": {"large": "https://example.invalid/ch.jpg"},
}

REVISION = {
    "id": 1930857,
    "type": 1,
    "creator": {"username": "inchei", "nickname": "逃城狗"},
    "summary": "别名标注",
    "created_at": "2026-09-20T17:33:29+08:00",
}

COLLECTION = {
    "subject_id": 237,
    "subject_type": 2,
    "rate": 9,
    "type": 2,
    "ep_status": 1,
    "vol_status": 0,
    "private": False,
    "tags": ["科幻"],
    "updated_at": "2026-09-20T17:33:29+08:00",
}


def handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    method = request.method
    if path == "/v0/search/subjects":
        body = json_body(request)
        assert body["filter"]["tag"] == ["科幻"]
        assert "nsfw" not in body["filter"]
        return httpx.Response(
            200, json={"total": 1, "limit": 1, "offset": 0, "data": [SUBJECT]}
        )
    if path == "/v0/subjects/237":
        return httpx.Response(200, json=SUBJECT)
    if path == "/v0/subjects/237/characters":
        return httpx.Response(200, json=[RELATED_CHARACTER])
    if path == "/v0/subjects/237/subjects":
        return httpx.Response(200, json=[])
    if path == "/v0/episodes":
        return httpx.Response(
            200, json={"total": 1, "limit": 100, "offset": 0, "data": [EPISODE]}
        )
    if path == "/v0/users/sai/collections/237":
        return httpx.Response(200, json=COLLECTION)
    if path == "/v0/users/-/collections/237":
        if method == "POST":
            return httpx.Response(204)
    if path == "/v0/users/-/collections/237/episodes":
        if method == "PATCH":
            body = json_body(request)
            assert body == {"episode_id": [96821, 96822], "type": 2}
            return httpx.Response(204)
    if path == "/v0/revisions/characters":
        assert request.url.params["character_id"] == "1"
        return httpx.Response(
            200, json={"total": 1, "limit": 30, "offset": 0, "data": [REVISION]}
        )
    if path == "/v0/subjects/999":
        return httpx.Response(
            404,
            json={"title": "Not Found", "description": "resource can't be found"},
        )
    raise AssertionError(f"unexpected request: {method} {path}")


@pytest.mark.anyio
async def test_tool_catalogue_is_small_and_documented() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            tools = (await c.list_tools()).tools
            names = {tool.name for tool in tools}
            assert names == {
                "bangumi_search",
                "bangumi_browse_subjects",
                "bangumi_get_subject",
                "bangumi_get_episodes",
                "bangumi_get_entity",
                "bangumi_get_revisions",
                "bangumi_get_user",
                "bangumi_get_calendar",
                "bangumi_get_collections",
                "bangumi_update_collection",
                "bangumi_manage_index",
            }
            for tool in tools:
                assert tool.title
                assert tool.output_schema
                assert tool.annotations is not None
            writable = {
                tool.name: tool.annotations.read_only_hint for tool in tools
            }
            assert writable["bangumi_get_subject"] is True
            assert writable["bangumi_update_collection"] is False
    finally:
        await client.close()


@pytest.mark.anyio
async def test_search_subject_maps_tags_to_api_key() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_search",
                {"keyword": "攻壳机动队", "limit": 1, "tags": ["科幻"]},
            )
            assert result.is_error is False
            payload = result.structured_content["result"]
            assert payload["entity"] == "subject"
            assert payload["data"][0]["id"] == 237
            assert payload["data"][0]["tags"][0]["total_count"] == 20
    finally:
        await client.close()


@pytest.mark.anyio
async def test_get_subject_with_related_sections() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_get_subject",
                {"subject_id": 237, "include": ["characters", "episodes"]},
            )
            assert result.is_error is False
            payload = result.structured_content
            assert payload["subject"]["name_cn"] == "攻壳机动队"
            assert payload["characters"][0]["relation"] == "主角"
            assert payload["episodes"][0]["id"] == 96821
            # Sections that were not requested stay absent after null pruning.
            assert "persons" not in payload
            assert "relations" not in payload
    finally:
        await client.close()


@pytest.mark.anyio
async def test_read_single_collection() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_get_collections",
                {"resource": "subject", "username": "sai", "subject_id": 237},
            )
            assert result.is_error is False
            payload = result.structured_content["result"]
            assert payload["collection"]["rate"] == 9
    finally:
        await client.close()


@pytest.mark.anyio
async def test_update_subject_collection_payload() -> None:
    captured: dict = {}

    def local_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v0/users/-/collections/237":
            captured.update(json_body(request))
            return httpx.Response(204)
        raise AssertionError(f"unexpected request: {request.method} {request.url.path}")

    client, mcp = make_server(local_handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_update_collection",
                {
                    "resource": "subject",
                    "subject_id": 237,
                    "status": 3,
                    "rating": 9,
                    "comment": "神作",
                    "tags": ["科幻"],
                },
            )
            assert result.is_error is False
            assert captured == {
                "type": 3,
                "rate": 9,
                "comment": "神作",
                "tags": ["科幻"],
            }
    finally:
        await client.close()


@pytest.mark.anyio
async def test_update_episode_batch_payload() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_update_collection",
                {
                    "resource": "episode",
                    "subject_id": 237,
                    "episode_ids": [96821, 96822],
                    "status": 2,
                },
            )
            assert result.is_error is False
    finally:
        await client.close()


@pytest.mark.anyio
async def test_revision_list_uses_entity_query_key() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_get_revisions",
                {"entity": "character", "entity_id": 1, "limit": 30},
            )
            assert result.is_error is False
            payload = result.structured_content
            assert payload["data"][0]["summary"] == "别名标注"
    finally:
        await client.close()


@pytest.mark.anyio
async def test_api_error_becomes_tool_error() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool("bangumi_get_subject", {"subject_id": 999})
            assert result.is_error is True
            assert "404" in result.content[0].text
    finally:
        await client.close()


@pytest.mark.anyio
async def test_validation_error_is_readable() -> None:
    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool("bangumi_get_episodes", {})
            assert result.is_error is True
            assert "exactly one of subject_id or episode_id" in result.content[0].text
    finally:
        await client.close()


@pytest.mark.anyio
async def test_network_error_becomes_readable_tool_error() -> None:
    def network_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client, mcp = make_server(network_handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool("bangumi_get_calendar", {})
            assert result.is_error is True
            assert "Network error" in result.content[0].text
    finally:
        await client.close()


@pytest.mark.anyio
async def test_character_uncollect_explains_upstream_gap() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "DELETE" and request.url.path == "/v0/characters/1/collect":
            return httpx.Response(
                404,
                json={
                    "title": "Not Found",
                    "details": {"path": "/v0/characters/1/collect", "method": "DELETE"},
                    "description": "This is default response, if you see this response, please check your request",
                },
            )
        raise AssertionError(f"unexpected request: {request.method} {request.url.path}")

    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_update_collection",
                {"resource": "character", "character_id": 1, "action": "unset"},
            )
            assert result.is_error is True
            assert "does not implement uncollecting characters" in result.content[0].text
    finally:
        await client.close()


@pytest.mark.anyio
async def test_manage_index_create_flow() -> None:
    created = {"id": 105410, "title": "", "desc": "", "total": 0}
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v0/indices":
            assert json_body(request) == {}
            return httpx.Response(200, json=created)
        if request.method == "PUT" and request.url.path == "/v0/indices/105410":
            captured.update(json_body(request))
            return httpx.Response(204)
        if request.method == "GET" and request.url.path == "/v0/indices/105410":
            return httpx.Response(
                200,
                json={**created, "title": captured.get("title", ""), "desc": captured.get("description", "")},
            )
        raise AssertionError(f"unexpected request: {request.method} {request.url.path}")

    client, mcp = make_server(handler)
    try:
        async with Client(mcp) as c:
            result = await c.call_tool(
                "bangumi_manage_index",
                {
                    "action": "create",
                    "title": "Bangumi-MCP write:indices test (safe to delete)",
                    "description": "temporary",
                },
            )
            assert result.is_error is False
            index = result.structured_content["index"]
            assert index["id"] == 105410
            assert index["title"] == "Bangumi-MCP write:indices test (safe to delete)"
            assert captured == {
                "title": "Bangumi-MCP write:indices test (safe to delete)",
                "description": "temporary",
            }
    finally:
        await client.close()
