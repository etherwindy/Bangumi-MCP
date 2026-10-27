# Bangumi MCP

[![License](https://img.shields.io/github/license/etherwindy/Bangumi-MCP)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-2.x-orange)](https://modelcontextprotocol.io)

[中文版本](README_zh.md)

<p align="center">
  <img src="https://placehold.co/200x200/transparent/pink?font=Oswald&text=Bangumi\nM%20C%20P" alt="Bangumi MCP Logo" width="256" height="256">
</p>

<p align="center">
  A Model Context Protocol server for the Bangumi API
</p>

Bangumi MCP gives MCP clients access to [Bangumi](https://bgm.tv) (bgm.tv):
anime, manga, books, music, games, characters, staff, indices and personal
collections.

The project is built on the **MCP Python SDK 2.3** (protocol revision
**2026-07-28**) and tracks the **2026-07-24** revision of the
[Bangumi OpenAPI document](https://bangumi.github.io/api/) bundled at
`bangumi_mcp/dist.json`.

## Highlights

- **11 intent-based tools** instead of one tool per REST endpoint. Each tool
  covers a whole workflow, so the catalogue stays small without losing access
  to any of the 56 operations exposed by the 47 Bangumi API paths.
- **Generated, validated schemas**: inputs come from Python type hints and
  outputs from Pydantic models. Clients receive `outputSchema` and
  `structuredContent` and can validate results themselves.
- **MCP 2.x features**: tool annotations, cache hints, resources, prompts,
  progress reporting, Streamable HTTP (stateful or stateless) and legacy SSE.
- **Bangumi-aware**: correct `filter.tag` search payloads, batched episode
  updates, token-scope hints, retries for rate limits and public reads that
  keep working when the configured token has expired.

## Quick start

```bash
git clone https://github.com/etherwindy/Bangumi-MCP.git
cd Bangumi-MCP
uv sync
uv run bangumi-mcp --help
```

Set a Bangumi access token (optional for public reads, required for `/v0/me`
and every write):

```env
# .env
BANGUMI_API_TOKEN=your_api_token_here
```

Create tokens at <https://next.bgm.tv/demo/access-token>. The current Bangumi
spec marks mutating endpoints with OAuth scopes:

| Scope              | Needed for                                                   |
| ------------------ | ------------------------------------------------------------ |
| `write:collection` | subject/episode collections, collect character/person/index  |
| `write:indices`    | creating/editing indices and their subjects                  |

A 403 answer includes a hint telling you which scope is missing.

## Tools

All tools are annotated with `readOnlyHint`, `destructiveHint`,
`idempotentHint` and `openWorldHint`.

| Tool | What it does | Bangumi endpoints |
| ---- | ------------ | ----------------- |
| `bangumi_search` | Search subjects, characters or persons by keyword. Subject search supports type, tags, meta tags, air date, rating, rating count, rank and NSFW filters. | `POST /v0/search/{subjects,characters,persons}` |
| `bangumi_browse_subjects` | Browse subjects by type/category/year/month/platform/series, sorted by date or rank. | `GET /v0/subjects` |
| `bangumi_get_subject` | Subject detail (summary, infobox, rating, tags, images, collection counts). `include` adds characters, staff, related subjects and/or episodes in one call. | `GET /v0/subjects/{id}` + related endpoints |
| `bangumi_get_episodes` | List a subject's episodes or fetch one episode. | `GET /v0/episodes`, `GET /v0/episodes/{id}` |
| `bangumi_get_entity` | Character or person detail; `include` adds their works and linked characters/persons. | `GET /v0/{characters,persons}/{id}` + related endpoints |
| `bangumi_get_revisions` | Revision history or one revision's diff payload for subject/episode/character/person. | `GET /v0/revisions/*` |
| `bangumi_get_user` | A user profile by username, or the authenticated user when `username` is omitted. | `GET /v0/users/{username}`, `GET /v0/me` |
| `bangumi_get_collections` | Read subject/character/person collections (any user) and the authenticated user's episode progress. | `GET /v0/users/*/collections*` |
| `bangumi_update_collection` | Write collection state: subject status/rating/comment/tags/progress, batch or single episode status, collect/uncollect character/person/index. | `POST/PATCH /v0/users/-/collections*`, `POST/DELETE /v0/*/collect` |
| `bangumi_manage_index` | Create/read/update indices, list/add/edit/remove index subjects, collect/uncollect an index. | `/v0/indices*` |
| `bangumi_get_calendar` | Weekly broadcast schedule of currently airing anime. | `GET /calendar` |

Image URLs are part of the subject/character/person/user payloads, so there is
no separate image tool. `bangumi_get_subject(subject_id=..., include=[...])`
replaces the old `get_subject_info` / `get_subject_persons` /
`get_subject_characters` / `get_subject_relations` family.

### Migrating from 0.1.x

The 55 endpoint tools were consolidated into the 11 tools above. No
functionality was dropped.

| Old tools | New tool |
| --------- | -------- |
| `search_subjects`, `search_characters`, `search_persons` | `bangumi_search` |
| `get_subjects` | `bangumi_browse_subjects` |
| `get_subject_info`, `get_subject_image`, `get_subject_persons`, `get_subject_characters`, `get_subject_relations` | `bangumi_get_subject` (`include=[...]`; images are in the payload) |
| `get_episodes`, `get_episode_info` | `bangumi_get_episodes` (`subject_id` or `episode_id`) |
| `search_characters`, `search_persons` | `bangumi_search` (`entity=character|person`) |
| `get_character_info`, `get_character_image`, `get_character_subjects`, `get_character_persons` | `bangumi_get_entity` (`entity=character`, `include=[...]`) |
| `get_person_info`, `get_person_image`, `get_person_subjects`, `get_person_characters` | `bangumi_get_entity` (`entity=person`, `include=[...]`) |
| `get_subject_revisions`, `get_subject_revision_info` and the six other revision tools | `bangumi_get_revisions` |
| `get_user_info`, `get_user_avatar`, `get_me_info` | `bangumi_get_user` |
| `get_user_collections`, `get_user_collection_info`, `get_my_episode_collections`, `get_my_episode_collection_info`, `get_user_character_collections*`, `get_user_person_collections*` | `bangumi_get_collections` |
| `post_my_collection`, `patch_my_collection`, `patch_my_episode_collections`, `put_my_episode_collection_info`, `post/delete_character_collection`, `post/delete_person_collection`, `post/delete_index_collection` | `bangumi_update_collection` |
| All nine index tools | `bangumi_manage_index` (`action=...`) |
| `get_calendar` | `bangumi_get_calendar` |
| `get_current_time` | removed — hosts already know the current time |

## MCP features in use

- **SDK 2.x / `MCPServer`** — the high-level server class (formerly
  `FastMCP`). Handlers are typed functions; schemas are generated from type
  hints, not maintained by hand.
- **Protocol 2026-07-28** — no handshake and no session on modern
  connections, `tools/list` cache hints, `resources/read` cache hints and
  per-request routing headers. The same process still serves 2025-era clients
  (including the legacy HTTP+SSE transport).
- **Structured output** — each tool declares an `outputSchema`; results are
  returned as both text and `structuredContent`. The client validates
  structured content, which is why nullable Bangumi fields are modelled as
  nullable and `null` values are dropped from payloads.
- **Annotations and titles** — every tool carries human-readable titles and
  MCP hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`,
  `openWorldHint`).
- **Resources** — `bangumi://calendar` plus `bangumi://subject/{id}`,
  `bangumi://character/{id}`, `bangumi://person/{id}` and
  `bangumi://user/{username}` templates let clients attach Bangumi data
  without tool calls.
- **Prompts** — `bangumi_recommend`, `bangumi_subject_deep_dive` and
  `bangumi_backlog_review` provide ready-made workflows.
- **Progress** — multi-fetch tools (`bangumi_get_subject`,
  `bangumi_get_entity`) report progress while loading related sections.
- **Transport control** — `--stateless` for session-less Streamable HTTP and
  `--json-response` for clients that prefer JSON over SSE streams.

## Configuration

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `BANGUMI_API_TOKEN` | unset | Bangumi access token. Public reads work without it. |
| `BANGUMI_API_BASE_URL` | `https://api.bgm.tv` | Override the API root (proxy/testing). |

`.env` files in the working directory are loaded automatically. If a token is
present but expired, public reads automatically retry anonymously; only
authenticated calls fail, with a hint pointing at the token page.

## Usage

### STDIO

```json
{
  "mcpServers": {
    "Bangumi-MCP": {
      "command": "uv",
      "args": ["--directory", "/path/to/Bangumi-MCP", "run", "bangumi-mcp"],
      "env": {
        "BANGUMI_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Streamable HTTP

```bash
uv run bangumi-mcp --mode=streamable_http --host localhost --port 18080
```

```json
{
  "mcpServers": {
    "Bangumi-MCP": {
      "type": "streamableHttp",
      "url": "http://localhost:18080/mcp"
    }
  }
}
```

Add `--stateless` to avoid server-side sessions entirely, or
`--json-response` to receive plain JSON responses.

### SSE (legacy clients)

```bash
uv run bangumi-mcp --mode=sse --host localhost --port 18080
```

```json
{
  "mcpServers": {
    "Bangumi-MCP": {
      "type": "sse",
      "url": "http://localhost:18080/sse"
    }
  }
}
```

SSE exists for clients that still use the 2025-era handshake. New clients
should use Streamable HTTP.

## Development

```bash
uv sync
uv run pytest
uv run python scripts/update_openapi.py --check   # is the bundled schema stale?
uv run python scripts/update_openapi.py           # refresh it
```

Layout:

```text
bangumi_mcp/
  __main__.py        CLI (stdio / sse / streamable_http)
  mcp_server.py      MCPServer factory, transports, cache hints
  bangumi_client.py  httpx client, retries, error mapping
  models.py          Pydantic models used for output schemas
  resources.py       MCP resources
  prompts.py         MCP prompts
  tools/             one module per tool group
scripts/update_openapi.py
tests/
```

When refreshing the OpenAPI document, review the diff and update
`bangumi_mcp/models.py`, `bangumi_client.py` and the tool descriptions if an
endpoint or payload changed.

## Acknowledgements

Originally built with the assistance of Qwen3-Coder and Claude Sonnet 4.

## License

MIT — see [LICENSE](LICENSE).
