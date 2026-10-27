"""Unified search and subject browsing tools."""

from __future__ import annotations

from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import (
    CharacterSearchResult,
    Page,
    PersonSearchResult,
    SearchResult,
    Subject,
    SubjectSearchResult,
)

from . import READ_ONLY, ensure_ok

SubjectType = Literal[1, 2, 3, 4, 6]
PersonCareer = Literal[
    "producer", "mangaka", "artist", "seiyu", "writer", "illustrator", "actor"
]


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_search",
        title="Search Bangumi",
        description=(
            "Search Bangumi by keyword. `entity=subject` searches anime, manga, "
            "books, music, games and live-action titles and accepts subject "
            "filters; `entity=character` searches characters; `entity=person` "
            "searches real people (staff, voice actors, authors). "
            "Use `bangumi_browse_subjects` for 'latest/ranked by year' browsing "
            "without a keyword."
        ),
        annotations=READ_ONLY,
    )
    async def search(
        keyword: Annotated[str, Field(description="Search keyword (Chinese, Japanese or English)")],
        entity: Annotated[
            Literal["subject", "character", "person"],
            Field(description="What to search: subject, character or person"),
        ] = "subject",
        limit: Annotated[int, Field(ge=1, le=50, description="Page size (max 50)")] = 20,
        offset: Annotated[int, Field(ge=0, description="Pagination offset")] = 0,
        sort: Annotated[
            Literal["match", "heat", "rank", "score"] | None,
            Field(description="Subject ordering: match (relevance), heat, rank or score"),
        ] = None,
        subject_types: Annotated[
            list[SubjectType] | None,
            Field(description="Subject only: restrict to these subject types (OR)"),
        ] = None,
        tags: Annotated[
            list[str] | None,
            Field(description="Subject only: require all of these tags; prefix a tag with '-' to exclude it"),
        ] = None,
        meta_tags: Annotated[
            list[str] | None,
            Field(description="Subject only: require all of these meta tags"),
        ] = None,
        air_date: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Subject only: air/release date range clauses, all must match. "
                    "Each clause is an operator plus a YYYY-MM-DD date, e.g. "
                    "['>=2024-01-01', '<2024-04-01']"
                )
            ),
        ] = None,
        rating: Annotated[
            list[str] | None,
            Field(description="Subject only: rating range clauses, e.g. ['>=8', '<9']"),
        ] = None,
        rating_count: Annotated[
            list[str] | None,
            Field(description="Subject only: rating-count clauses, e.g. ['>=200', '<5000']"),
        ] = None,
        rank: Annotated[
            list[str] | None,
            Field(description="Subject only: rank range clauses, e.g. ['<=1000']"),
        ] = None,
        nsfw: Annotated[
            bool | None,
            Field(
                description=(
                    "NSFW filter: omit for both, true for NSFW only, false for "
                    "SFW only (ignored without permission)"
                )
            ),
        ] = None,
        career: Annotated[
            list[PersonCareer] | None,
            Field(description="Person only: require all of these careers"),
        ] = None,
    ) -> SearchResult:
        if entity == "subject":
            filters: dict[str, object] = {}
            if subject_types:
                filters["type"] = subject_types
            if tags:
                filters["tag"] = tags
            if meta_tags:
                filters["meta_tags"] = meta_tags
            if air_date:
                filters["air_date"] = air_date
            if rating:
                filters["rating"] = rating
            if rating_count:
                filters["rating_count"] = rating_count
            if rank:
                filters["rank"] = rank
            if nsfw is not None:
                filters["nsfw"] = nsfw
            params: dict[str, object] = {
                "keyword": keyword,
                "limit": limit,
                "offset": offset,
            }
            if sort:
                params["sort"] = sort
            if filters:
                params["filter"] = filters
            status, payload = await client.search_subjects(params)
            ensure_ok(status, payload)
            return SubjectSearchResult.model_validate(payload)

        if entity == "character":
            params = {"keyword": keyword, "limit": limit, "offset": offset}
            if nsfw is not None:
                params["filter"] = {"nsfw": nsfw}
            status, payload = await client.search_characters(params)
            ensure_ok(status, payload)
            return CharacterSearchResult.model_validate(payload)

        params = {"keyword": keyword, "limit": limit, "offset": offset}
        if career:
            params["filter"] = {"career": career}
        status, payload = await client.search_persons(params)
        ensure_ok(status, payload)
        return PersonSearchResult.model_validate(payload)

    @mcp.tool(
        name="bangumi_browse_subjects",
        title="Browse Bangumi subjects",
        description=(
            "Browse subjects without a keyword: filter by subject type and "
            "category, year/month, platform or book series, then sort by air "
            "date or rank. Useful for 'best anime of 2024' or 'this season's "
            "TV anime' style requests."
        ),
        annotations=READ_ONLY,
    )
    async def browse_subjects(
        subject_type: Annotated[
            SubjectType,
            Field(description="Subject type (required): 1=book, 2=anime, 3=music, 4=game, 6=real"),
        ],
        category: Annotated[
            int | None,
            Field(
                description=(
                    "Category id. Books: 1001 manga, 1002 novel, 1003 art book; "
                    "anime: 1 TV, 2 OVA, 3 movie, 5 web; games: 4001 game, 4002 "
                    "software, 4003 DLC, 4005 tabletop; real: 1 jdrama, 2 "
                    "western, 3 chinese, 6001 TV series, 6002 movie, 6003 stage, "
                    "6004 variety"
                )
            ),
        ] = None,
        series: Annotated[
            bool | None, Field(description="Books only: browse a book series")
        ] = None,
        platform: Annotated[
            str | None, Field(description="Games only: platform name")
        ] = None,
        sort: Annotated[
            Literal["date", "rank"] | None,
            Field(description="Order by air/release date or by rank"),
        ] = None,
        year: Annotated[int | None, Field(ge=1900, le=2100, description="Year filter")] = None,
        month: Annotated[int | None, Field(ge=1, le=12, description="Month filter (1-12)")] = None,
        limit: Annotated[int, Field(ge=1, le=50, description="Page size (max 50)")] = 20,
        offset: Annotated[int, Field(ge=0, description="Pagination offset")] = 0,
    ) -> Page[Subject]:
        params: dict[str, object] = {
            "type": subject_type,
            "limit": limit,
            "offset": offset,
        }
        for key, value in {
            "cat": category,
            "series": series,
            "platform": platform,
            "sort": sort,
            "year": year,
            "month": month,
        }.items():
            if value is not None:
                params[key] = value
        status, payload = await client.get_subjects(params)
        ensure_ok(status, payload)
        return Page[Subject].model_validate(payload)
