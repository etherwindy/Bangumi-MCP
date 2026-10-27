"""HTTP client for the Bangumi API (https://bangumi.github.io/api/).

The client targets the ``2026-07-24`` revision of the OpenAPI document bundled
in :mod:`bangumi_mcp.dist` and is deliberately small: every method returns a
``(status_code, payload)`` tuple so callers can decide how to surface errors.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

from bangumi_mcp import __version__

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.bgm.tv"
DEFAULT_TIMEOUT = 20.0
DEFAULT_RETRIES = 2

#: Status codes worth retrying. 429 is retried for every method because the
#: request was rejected, not processed; 5xx is only retried for safe methods.
_RETRY_STATUS = {429, 502, 503, 504}
_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

_TOKEN_URL = "https://next.bgm.tv/demo/access-token"

_SCOPE_HINTS = {
    401: (
        "Bangumi API token missing or invalid. Set the BANGUMI_API_TOKEN "
        f"environment variable with a token from {_TOKEN_URL}."
    ),
    403: (
        "The Bangumi API token is not allowed to perform this action. "
        "Mutating endpoints now require the `write:collection` or "
        f"`write:indices` scope; create a token with those scopes at {_TOKEN_URL}."
    ),
}


class BangumiAPIError(Exception):
    """Raised when a response cannot be interpreted as a Bangumi payload."""

    def __init__(self, status_code: int, payload: Any, url: str = "") -> None:
        self.status_code = status_code
        self.payload = payload
        self.url = url
        title = payload.get("title") if isinstance(payload, dict) else None
        description = payload.get("description") if isinstance(payload, dict) else None
        super().__init__(
            f"Bangumi API request failed ({status_code}): "
            f"{title or description or payload!r}"
        )


def _error_payload(status_code: int, payload: Any, url: str) -> Dict[str, Any]:
    """Turn any non-2xx body into a compact, LLM-readable error object."""
    data: Dict[str, Any] = {"status": status_code, "url": url}
    if isinstance(payload, dict):
        data.update(payload)
    elif payload:
        data["details"] = payload
    if hint := _SCOPE_HINTS.get(status_code):
        data.setdefault("hint", hint)
    return data


def _parse_json(response: httpx.Response) -> Any:
    if not response.content:
        return {}
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"raw": response.text[:2000]}


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass
    return min(2.0, 0.25 * (2**attempt))


def _clean_params(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Drop ``None`` values so optional query parameters are really optional."""
    return {k: v for k, v in (params or {}).items() if v is not None}


class BangumiClient:
    """Async client for the Bangumi API."""

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        """Create a client.

        Args:
            token: Bangumi API access token. Falls back to ``BANGUMI_API_TOKEN``
                (loaded from ``.env`` when present).
            base_url: API root, defaults to ``BANGUMI_API_BASE_URL`` or
                ``https://api.bgm.tv``.
            timeout: Per-request timeout in seconds.
            retries: Number of retries for rate-limited/failed requests.
            transport: Optional httpx transport (used by tests).
        """
        load_dotenv()
        self.token = token or os.getenv("BANGUMI_API_TOKEN") or None
        self.base_url = (
            base_url or os.getenv("BANGUMI_API_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout
        self.retries = max(0, retries)

        headers = {
            "User-Agent": (
                f"etherwindy/Bangumi-MCP v{__version__} "
                "(+https://github.com/etherwindy/Bangumi-MCP)"
            ),
            "Accept": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
            transport=transport,
        )

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self.client.aclose()

    async def __aenter__(self) -> "BangumiClient":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.close()

    def _auth_headers(self) -> Dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    # ------------------------------------------------------------------
    # transport helpers
    # ------------------------------------------------------------------
    async def _send(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]],
        json_body: Optional[Dict[str, Any]],
        auth: bool,
    ) -> httpx.Response:
        headers = self._auth_headers() if auth else {}
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        return await self.client.request(
            method,
            url,
            params=_clean_params(params),
            json=json_body,
            headers=headers,
        )

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        public: bool = False,
    ) -> tuple[int, Any]:
        method = method.upper()
        last_response: Optional[httpx.Response] = None
        last_error: Optional[httpx.TransportError] = None
        for attempt in range(self.retries + 1):
            try:
                response = await self._send(
                    method, url, params=params, json_body=json_body, auth=True
                )
            except httpx.TransportError as exc:
                last_error = exc
                if attempt == self.retries:
                    break
                delay = min(2.0, 0.25 * (2**attempt))
                logger.debug(
                    "Bangumi API %s %s failed (%s), retrying in %.2fs",
                    method,
                    url,
                    type(exc).__name__,
                    delay,
                )
                await asyncio.sleep(delay)
                continue
            last_response = response
            retryable = response.status_code in _RETRY_STATUS and (
                response.status_code == 429 or method in _SAFE_METHODS
            )
            if not retryable or attempt == self.retries:
                break
            delay = _retry_delay(response, attempt)
            logger.debug(
                "Bangumi API %s %s returned %s, retrying in %.2fs",
                method,
                url,
                response.status_code,
                delay,
            )
            await asyncio.sleep(delay)

        if last_response is None:
            # Connection/DNS/TLS/proxy failure after retries. Report it as a
            # normal structured API error so the model sees a useful message.
            message = (
                f"{type(last_error).__name__}: {last_error}"
                if last_error
                else "request failed"
            )
            return 0, {
                "title": "Network error",
                "description": message,
                "hint": (
                    "Check network connectivity or proxy settings, then retry. "
                    f"Endpoint: {method} {url}"
                ),
            }
        if last_response.status_code == 401 and self.token and public:
            # An expired/invalid token must not break public read-only data.
            logger.warning(
                "Bangumi API rejected BANGUMI_API_TOKEN for %s %s; retrying anonymously",
                method,
                url,
            )
            try:
                last_response = await self._send(
                    method, url, params=params, json_body=json_body, auth=False
                )
            except httpx.TransportError as exc:
                return 0, {
                    "title": "Network error",
                    "description": str(exc),
                    "hint": f"Anonymous retry failed for {method} {url}",
                }
        payload = _parse_json(last_response)
        if last_response.status_code >= 400:
            payload = _error_payload(
                last_response.status_code, payload, str(last_response.url)
            )
        return last_response.status_code, payload

    async def _get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        public: bool = True,
    ) -> tuple[int, Any]:
        """GET a URL. Most Bangumi GET endpoints are public; pass ``public=False``
        for endpoints that must never be retried anonymously."""
        return await self._request("GET", url, params=params, public=public)

    async def _post(
        self,
        url: str,
        json_body: Optional[Dict[str, Any]] = None,
        *,
        public: bool = False,
    ) -> tuple[int, Any]:
        return await self._request(
            "POST", url, json_body=json_body, public=public
        )

    async def _put(
        self, url: str, json_body: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Any]:
        return await self._request("PUT", url, json_body=json_body)

    async def _patch(
        self, url: str, json_body: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Any]:
        return await self._request("PATCH", url, json_body=json_body)

    async def _delete(self, url: str) -> tuple[int, Any]:
        return await self._request("DELETE", url)

    async def _get_redirect_url(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Any]:
        """Follow image redirects and return ``{"url": ...}``."""
        try:
            response = await self.client.get(
                url,
                params=_clean_params(params),
                headers=self._auth_headers(),
                follow_redirects=False,
            )
        except httpx.TransportError as exc:
            return 0, {
                "title": "Network error",
                "description": f"{type(exc).__name__}: {exc}",
                "hint": f"Image request failed: {url}",
            }
        if response.is_redirect:
            return response.status_code, {
                "url": response.headers.get("Location", "")
            }
        payload = _parse_json(response)
        if response.status_code >= 400:
            payload = _error_payload(
                response.status_code, payload, str(response.url)
            )
        return response.status_code, payload

    # ------------------------------------------------------------------
    # request normalisation
    # ------------------------------------------------------------------
    @staticmethod
    def _normalise_subject_search(params: Dict[str, Any]) -> Dict[str, Any]:
        """Map the tool-facing search payload onto the current API contract.

        The subject search endpoint accepts ``filter.tag`` (singular). Older
        versions of this server exposed ``filter.tags``; keep accepting it
        while emitting the key the API actually documents. ``nsfw`` is left
        out when unset because ``null`` means "both NSFW and SFW".
        """
        payload = dict(params or {})
        body: Dict[str, Any] = {"keyword": payload.get("keyword", "")}
        if payload.get("sort"):
            body["sort"] = payload["sort"]
        filters = dict(payload.get("filter") or {})
        if "tags" in filters and "tag" not in filters:
            filters["tag"] = filters.pop("tags")
        if filters.get("nsfw") is None:
            filters.pop("nsfw", None)
        if filters:
            body["filter"] = filters
        return body

    # ------------------------------------------------------------------
    # calendar
    # ------------------------------------------------------------------
    async def get_calendar(self) -> tuple[int, Any]:
        return await self._get("/calendar")

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------
    async def search_subjects(self, params: Dict[str, Any]) -> tuple[int, Any]:
        body = self._normalise_subject_search(params)
        query = _clean_params(
            {"limit": params.get("limit"), "offset": params.get("offset")}
        )
        return await self._request(
            "POST", "/v0/search/subjects", params=query, json_body=body, public=True
        )

    async def search_characters(self, params: Dict[str, Any]) -> tuple[int, Any]:
        body: Dict[str, Any] = {"keyword": params.get("keyword", "")}
        filters = {
            k: v for k, v in (params.get("filter") or {}).items() if v is not None
        }
        if filters:
            body["filter"] = filters
        query = _clean_params(
            {"limit": params.get("limit"), "offset": params.get("offset")}
        )
        return await self._request(
            "POST", "/v0/search/characters", params=query, json_body=body, public=True
        )

    async def search_persons(self, params: Dict[str, Any]) -> tuple[int, Any]:
        body: Dict[str, Any] = {"keyword": params.get("keyword", "")}
        filters = {
            k: v for k, v in (params.get("filter") or {}).items() if v is not None
        }
        if filters:
            body["filter"] = filters
        query = _clean_params(
            {"limit": params.get("limit"), "offset": params.get("offset")}
        )
        return await self._request(
            "POST", "/v0/search/persons", params=query, json_body=body, public=True
        )

    # ------------------------------------------------------------------
    # subjects
    # ------------------------------------------------------------------
    async def get_subjects(self, params: Dict[str, Any]) -> tuple[int, Any]:
        # `day` was never part of the API; drop it for older clients.
        allowed = {
            "type",
            "cat",
            "series",
            "platform",
            "sort",
            "year",
            "month",
            "limit",
            "offset",
        }
        query = {k: v for k, v in (params or {}).items() if k in allowed}
        return await self._get("/v0/subjects", query)

    async def get_subject_info(self, subject_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/subjects/{subject_id}")

    async def get_subject_image(
        self, subject_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get_redirect_url(
            f"/v0/subjects/{subject_id}/image", params
        )

    async def get_subject_persons(self, subject_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/subjects/{subject_id}/persons")

    async def get_subject_characters(self, subject_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/subjects/{subject_id}/characters")

    async def get_subject_relations(self, subject_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/subjects/{subject_id}/subjects")

    # ------------------------------------------------------------------
    # episodes
    # ------------------------------------------------------------------
    async def get_episodes(self, params: Dict[str, Any]) -> tuple[int, Any]:
        if "episode_type" in params and "type" not in params:
            params = dict(params)
            params["type"] = params.pop("episode_type")
        return await self._get("/v0/episodes", params)

    async def get_episode_info(self, episode_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/episodes/{episode_id}")

    # ------------------------------------------------------------------
    # characters
    # ------------------------------------------------------------------
    async def get_character_info(self, character_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/characters/{character_id}")

    async def get_character_image(
        self, character_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get_redirect_url(
            f"/v0/characters/{character_id}/image", params
        )

    async def get_character_subjects(self, character_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/characters/{character_id}/subjects")

    async def get_character_persons(self, character_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/characters/{character_id}/persons")

    async def post_character_collection(
        self, character_id: int
    ) -> tuple[int, Any]:
        return await self._post(f"/v0/characters/{character_id}/collect")

    async def delete_character_collection(
        self, character_id: int
    ) -> tuple[int, Any]:
        return await self._delete(f"/v0/characters/{character_id}/collect")

    # ------------------------------------------------------------------
    # persons
    # ------------------------------------------------------------------
    async def get_person_info(self, person_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/persons/{person_id}")

    async def get_person_image(
        self, person_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get_redirect_url(
            f"/v0/persons/{person_id}/image", params
        )

    async def get_person_subjects(self, person_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/persons/{person_id}/subjects")

    async def get_person_characters(self, person_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/persons/{person_id}/characters")

    async def post_person_collection(self, person_id: int) -> tuple[int, Any]:
        return await self._post(f"/v0/persons/{person_id}/collect")

    async def delete_person_collection(self, person_id: int) -> tuple[int, Any]:
        return await self._delete(f"/v0/persons/{person_id}/collect")

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    async def get_user_info(self, username: str) -> tuple[int, Any]:
        return await self._get(f"/v0/users/{username}")

    async def get_user_avatar(
        self, username: str, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get_redirect_url(
            f"/v0/users/{username}/avatar", params
        )

    async def get_me_info(self) -> tuple[int, Any]:
        return await self._get("/v0/me", public=False)

    # ------------------------------------------------------------------
    # collections
    # ------------------------------------------------------------------
    async def get_user_collections(
        self, username: str, params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Any]:
        if not username:
            raise ValueError("username must be provided to get collections")
        return await self._get(f"/v0/users/{username}/collections", params)

    async def get_user_collection_info(
        self, username: str, subject_id: int
    ) -> tuple[int, Any]:
        return await self._get(f"/v0/users/{username}/collections/{subject_id}")

    async def post_my_collection(
        self, subject_id: int, params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Any]:
        return await self._post(
            f"/v0/users/-/collections/{subject_id}", params or {}
        )

    async def patch_my_collection(
        self, subject_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._patch(
            f"/v0/users/-/collections/{subject_id}", params
        )

    async def get_my_episode_collections(
        self, subject_id: int, params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Any]:
        if not subject_id:
            raise ValueError("subject_id must be provided")
        return await self._get(
            f"/v0/users/-/collections/{subject_id}/episodes",
            params,
            public=False,
        )

    async def patch_my_episode_collections(
        self, subject_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        body = dict(params)
        episode_id = body.get("episode_id")
        if episode_id is not None and not isinstance(episode_id, list):
            body["episode_id"] = [episode_id]
        return await self._patch(
            f"/v0/users/-/collections/{subject_id}/episodes", body
        )

    async def get_my_episode_collection_info(
        self, episode_id: int
    ) -> tuple[int, Any]:
        return await self._get(
            f"/v0/users/-/collections/-/episodes/{episode_id}", public=False
        )

    async def put_my_episode_collection_info(
        self, episode_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._put(
            f"/v0/users/-/collections/-/episodes/{episode_id}", params
        )

    async def get_user_character_collections(
        self, username: str
    ) -> tuple[int, Any]:
        if not username:
            raise ValueError("username must be provided")
        return await self._get(f"/v0/users/{username}/collections/-/characters")

    async def get_user_character_collection_info(
        self, username: str, character_id: int
    ) -> tuple[int, Any]:
        return await self._get(
            f"/v0/users/{username}/collections/-/characters/{character_id}"
        )

    async def get_user_person_collections(self, username: str) -> tuple[int, Any]:
        if not username:
            raise ValueError("username must be provided")
        return await self._get(f"/v0/users/{username}/collections/-/persons")

    async def get_user_person_collection_info(
        self, username: str, person_id: int
    ) -> tuple[int, Any]:
        return await self._get(
            f"/v0/users/{username}/collections/-/persons/{person_id}"
        )

    # ------------------------------------------------------------------
    # revisions
    # ------------------------------------------------------------------
    async def get_subject_revisions(
        self, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get("/v0/revisions/subjects", params)

    async def get_subject_revision_info(
        self, revision_id: int
    ) -> tuple[int, Any]:
        return await self._get(f"/v0/revisions/subjects/{revision_id}")

    async def get_episode_revisions(
        self, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get("/v0/revisions/episodes", params)

    async def get_episode_revision_info(
        self, revision_id: int
    ) -> tuple[int, Any]:
        return await self._get(f"/v0/revisions/episodes/{revision_id}")

    async def get_character_revisions(
        self, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get("/v0/revisions/characters", params)

    async def get_character_revision_info(
        self, revision_id: int
    ) -> tuple[int, Any]:
        return await self._get(f"/v0/revisions/characters/{revision_id}")

    async def get_person_revisions(
        self, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._get("/v0/revisions/persons", params)

    async def get_person_revision_info(
        self, revision_id: int
    ) -> tuple[int, Any]:
        return await self._get(f"/v0/revisions/persons/{revision_id}")

    # ------------------------------------------------------------------
    # indices
    # ------------------------------------------------------------------
    async def post_index(self) -> tuple[int, Any]:
        # The endpoint takes no documented body, but the server requires a
        # decodable JSON body; an empty object is the accepted form.
        return await self._post("/v0/indices", {})

    async def get_index_info(self, index_id: int) -> tuple[int, Any]:
        return await self._get(f"/v0/indices/{index_id}")

    async def put_index(
        self, index_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._put(f"/v0/indices/{index_id}", params)

    async def post_index_collection(self, index_id: int) -> tuple[int, Any]:
        return await self._post(f"/v0/indices/{index_id}/collect")

    async def delete_index_collection(self, index_id: int) -> tuple[int, Any]:
        return await self._delete(f"/v0/indices/{index_id}/collect")

    async def get_index_subjects(
        self, index_id: int, params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Any]:
        return await self._get(f"/v0/indices/{index_id}/subjects", params)

    async def post_index_subject(
        self, index_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._post(f"/v0/indices/{index_id}/subjects", params)

    async def put_index_subject(
        self, index_id: int, subject_id: int, params: Dict[str, Any]
    ) -> tuple[int, Any]:
        return await self._put(
            f"/v0/indices/{index_id}/subjects/{subject_id}", params
        )

    async def delete_index_subject(
        self, index_id: int, subject_id: int
    ) -> tuple[int, Any]:
        return await self._delete(
            f"/v0/indices/{index_id}/subjects/{subject_id}"
        )
