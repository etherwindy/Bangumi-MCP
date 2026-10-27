"""Calendar tool."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import CalendarOutput

from . import READ_ONLY, ensure_ok


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_get_calendar",
        title="Bangumi weekly anime calendar",
        description=(
            "Get Bangumi's weekly broadcast calendar: every currently airing "
            "anime grouped by weekday, with cover, score, rank and collection "
            "counts. Use it for 'what is airing today/this season' questions."
        ),
        annotations=READ_ONLY,
    )
    async def get_calendar() -> CalendarOutput:
        status, payload = await client.get_calendar()
        ensure_ok(status, payload)
        return CalendarOutput.model_validate({"calendar": payload})
