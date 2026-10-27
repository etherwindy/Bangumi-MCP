"""Unit tests for the HTTP client and models."""

from __future__ import annotations

import httpx
import pytest

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import Subject

from conftest import json_body, make_client


@pytest.mark.anyio
async def test_subject_search_normalisation() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json_body(request))
        return httpx.Response(200, json={"total": 0, "data": []})

    client = make_client(handler)
    try:
        status, _ = await client.search_subjects(
            {
                "keyword": "test",
                "limit": 5,
                "filter": {"tags": ["科幻"], "type": [2], "nsfw": None},
            }
        )
        assert status == 200
        assert captured["filter"] == {"tag": ["科幻"], "type": [2]}
        assert captured["keyword"] == "test"
    finally:
        await client.close()


@pytest.mark.anyio
async def test_episode_collection_normalises_single_id() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json_body(request))
        return httpx.Response(204)

    client = make_client(handler)
    try:
        status, _ = await client.patch_my_episode_collections(
            237, {"episode_id": 96821, "type": 2}
        )
        assert status == 204
        assert captured == {"episode_id": [96821], "type": 2}
    finally:
        await client.close()


@pytest.mark.anyio
async def test_public_read_falls_back_to_anonymous() -> None:
    calls: list[str | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("Authorization")
        calls.append(auth)
        if auth:
            return httpx.Response(401, json={"title": "Unauthorized"})
        return httpx.Response(200, json={"total": 1, "data": []})

    client = make_client(handler)
    try:
        status, payload = await client.search_subjects({"keyword": "x"})
        assert status == 200
        assert payload["total"] == 1
        assert len(calls) == 2
        assert calls[1] is None
    finally:
        await client.close()


@pytest.mark.anyio
async def test_private_endpoint_keeps_auth_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"title": "Unauthorized"})

    client = make_client(handler)
    try:
        status, payload = await client.get_me_info()
        assert status == 401
        assert "BANGUMI_API_TOKEN" in payload["hint"]
    finally:
        await client.close()


@pytest.mark.anyio
async def test_retry_on_rate_limit() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"ok": True})

    client = BangumiClient(token="test", transport=httpx.MockTransport(handler), retries=1)
    try:
        status, payload = await client.get_calendar()
        assert status == 200
        assert payload == {"ok": True}
        assert calls == 2
    finally:
        await client.close()


def test_models_keep_extra_fields_and_drop_nulls() -> None:
    subject = Subject.model_validate(
        {
            "id": 1,
            "name": "Test",
            "name_cn": None,
            "summary": None,
            "undefined_by_schema": {"kept": True},
        }
    )
    dumped = subject.model_dump(mode="json")
    assert dumped["id"] == 1
    assert "name_cn" not in dumped
    assert "summary" not in dumped
    assert dumped["undefined_by_schema"] == {"kept": True}


@pytest.mark.anyio
async def test_network_error_is_reported_as_structured_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = make_client(handler)
    try:
        status, payload = await client.get_calendar()
        assert status == 0
        assert payload["title"] == "Network error"
        assert "connection refused" in payload["description"]
    finally:
        await client.close()


@pytest.mark.anyio
async def test_post_index_sends_json_object_body() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["body"] = json_body(request)
        captured["content_type"] = request.headers.get("Content-Type")
        return httpx.Response(
            200,
            json={
                "id": 105410,
                "title": "",
                "desc": "",
                "total": 0,
                "creator": {"username": "tester", "nickname": "tester"},
            },
        )

    client = make_client(handler)
    try:
        status, payload = await client.post_index()
        assert status == 200
        assert captured == {
            "method": "POST",
            "path": "/v0/indices",
            "body": {},
            "content_type": "application/json",
        }
        assert payload["id"] == 105410
    finally:
        await client.close()
