"""Reusable prompt templates for Bangumi workflows."""

from __future__ import annotations

from typing import Annotated

from mcp.server.mcpserver import MCPServer
from pydantic import Field


def register(mcp: MCPServer) -> None:
    @mcp.prompt(
        name="bangumi_recommend",
        title="Recommend anime from Bangumi",
        description="Recommend currently airing or season-specific anime using Bangumi data.",
    )
    def recommend(
        taste: Annotated[
            str,
            Field(description="Free-form description of what the user likes (genres, moods, examples)"),
        ] = "",
        season: Annotated[
            str | None,
            Field(description="Optional season hint such as '2026 autumn' or a year"),
        ] = None,
    ) -> str:
        parts = [
            "You are an anime recommendation assistant with access to the Bangumi MCP tools.",
            "1. Call bangumi_get_calendar for currently airing shows" + (
                f", and bangumi_browse_subjects for the {season} season" if season else ""
            ) + ".",
            "2. Use bangumi_get_subject on promising candidates when you need staff, tags or scores.",
            "3. Rank candidates by fit with the user's taste, not only by Bangumi score.",
            "4. Return 5 recommendations. For each: title (Chinese + original), why it fits, "
            "score, rank and a one-line spoiler-free synopsis.",
        ]
        if taste:
            parts.append(f"User preferences: {taste}")
        return "\n".join(parts)

    @mcp.prompt(
        name="bangumi_subject_deep_dive",
        title="Deep dive into a Bangumi subject",
        description="Research a work, its staff, characters and related entries on Bangumi.",
    )
    def subject_deep_dive(
        title: Annotated[str, Field(description="Title of the anime/manga/game/book to research")],
    ) -> str:
        return (
            "You are a Bangumi research assistant.\n"
            f"Research the work named {title!r} using the Bangumi MCP tools:\n"
            "1. Call bangumi_search with entity=subject to find the best matching subject.\n"
            "2. Call bangumi_get_subject with include=['characters','persons','relations','episodes'].\n"
            "3. Call bangumi_get_episodes if the episode list is incomplete.\n"
            "Then produce: an overview (type, date, score, rank), the core staff, the main "
            "characters, related works in the franchise, and a watch/read order suggestion. "
            "Mark spoilers and keep synopsis details brief."
        )

    @mcp.prompt(
        name="bangumi_backlog_review",
        title="Review a Bangumi backlog",
        description="Summarise a user's watching/reading backlog and suggest what to pick next.",
    )
    def backlog_review(
        username: Annotated[
            str | None,
            Field(description="Bangumi username; omit to review the authenticated user"),
        ] = None,
    ) -> str:
        target = f"the Bangumi user {username!r}" if username else "the authenticated Bangumi user"
        return (
            f"Review the anime/manga backlog of {target}.\n"
            "1. Call bangumi_get_collections with resource=subject and status=1 (wish) "
            "or status=3 (doing), paging through the results.\n"
            "2. Group the backlog by subject type and by how long it has been waiting.\n"
            "3. Recommend the next 3 titles to pick up, with one sentence of reasoning each, "
            "and mention anything worth dropping."
        )
