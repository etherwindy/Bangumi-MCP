"""Index (目录) management tool."""

from __future__ import annotations

from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from bangumi_mcp.bangumi_client import BangumiClient
from bangumi_mcp.models import Index, IndexActionResult, IndexSubject, Page

from . import DESTRUCTIVE, ensure_ok

IndexAction = Literal[
    "create",
    "get",
    "update",
    "list_subjects",
    "add_subject",
    "update_subject",
    "remove_subject",
    "collect",
    "uncollect",
]
SubjectType = Literal[1, 2, 3, 4, 6]


def register(mcp: MCPServer, client: BangumiClient) -> None:
    @mcp.tool(
        name="bangumi_manage_index",
        title="Manage Bangumi indices",
        description=(
            "Work with Bangumi indices (user-curated subject lists): create, "
            "read, rename, add/edit/remove subjects, list subjects and "
            "collect/uncollect. Every action takes `index_id` except `create`; "
            "adding or editing subjects takes `subject_id`. Index edits require "
            "write:indices; collecting an index requires write:collection."
        ),
        annotations=DESTRUCTIVE,
    )
    async def manage_index(
        action: Annotated[IndexAction, Field(description="Operation to perform")],
        index_id: Annotated[int | None, Field(description="Index id (required except for create)")] = None,
        title: Annotated[str | None, Field(description="create/update: index title")] = None,
        description: Annotated[str | None, Field(description="create/update: index description")] = None,
        subject_id: Annotated[
            int | None, Field(description="add_subject/update_subject/remove_subject: subject id")
        ] = None,
        subject_type: Annotated[
            SubjectType | None, Field(description="list_subjects: filter by subject type")
        ] = None,
        sort: Annotated[
            int | None, Field(description="add_subject/update_subject: order in the index (smaller first)")
        ] = None,
        comment: Annotated[
            str | None, Field(description="add_subject/update_subject: note for the subject")
        ] = None,
        limit: Annotated[int, Field(ge=1, le=50, description="list_subjects page size")] = 30,
        offset: Annotated[int, Field(ge=0, description="list_subjects pagination offset")] = 0,
    ) -> IndexActionResult:
        if action != "create" and index_id is None:
            raise ToolError(f"{action} requires index_id")

        if action == "create":
            code, payload = await client.post_index()
            index = Index.model_validate(ensure_ok(code, payload))
            if title is not None or description is not None:
                body = {
                    k: v
                    for k, v in {"title": title, "description": description}.items()
                    if v is not None
                }
                code, _ = await client.put_index(index.id, body)
                ensure_ok(code, {})
                code, payload = await client.get_index_info(index.id)
                index = Index.model_validate(ensure_ok(code, payload))
            return IndexActionResult(
                action="create",
                message=f"Index {index.id} created.",
                index=index,
            )

        if action == "get":
            code, payload = await client.get_index_info(index_id)
            return IndexActionResult(
                action="get",
                message=f"Index {index_id}.",
                index=Index.model_validate(ensure_ok(code, payload)),
            )

        if action == "update":
            body = {
                k: v
                for k, v in {"title": title, "description": description}.items()
                if v is not None
            }
            if not body:
                raise ToolError("update requires title and/or description")
            code, payload = await client.put_index(index_id, body)
            ensure_ok(code, payload)
            code, payload = await client.get_index_info(index_id)
            return IndexActionResult(
                action="update",
                message=f"Index {index_id} updated.",
                index=Index.model_validate(ensure_ok(code, payload)),
            )

        if action == "list_subjects":
            params: dict[str, object] = {"limit": limit, "offset": offset}
            if subject_type is not None:
                params["type"] = subject_type
            code, payload = await client.get_index_subjects(index_id, params)
            body = ensure_ok(code, payload)
            page = Page[IndexSubject].model_validate(body)
            return IndexActionResult(
                action="list_subjects",
                message=f"Index {index_id} contains {page.total} subjects.",
                subjects=page,
            )

        if action == "add_subject":
            if subject_id is None:
                raise ToolError("add_subject requires subject_id")
            body = {"subject_id": subject_id}
            if sort is not None:
                body["sort"] = sort
            if comment is not None:
                body["comment"] = comment
            code, payload = await client.post_index_subject(index_id, body)
            ensure_ok(code, payload)
            return IndexActionResult(
                action="add_subject",
                message=f"Subject {subject_id} added to index {index_id}.",
            )

        if action == "update_subject":
            if subject_id is None:
                raise ToolError("update_subject requires subject_id")
            body = {k: v for k, v in {"sort": sort, "comment": comment}.items() if v is not None}
            if not body:
                raise ToolError("update_subject requires sort and/or comment")
            code, payload = await client.put_index_subject(index_id, subject_id, body)
            ensure_ok(code, payload)
            return IndexActionResult(
                action="update_subject",
                message=f"Subject {subject_id} updated in index {index_id}.",
            )

        if action == "remove_subject":
            if subject_id is None:
                raise ToolError("remove_subject requires subject_id")
            code, payload = await client.delete_index_subject(index_id, subject_id)
            ensure_ok(code, payload)
            return IndexActionResult(
                action="remove_subject",
                message=f"Subject {subject_id} removed from index {index_id}.",
            )

        if action == "collect":
            code, payload = await client.post_index_collection(index_id)
            ensure_ok(code, payload)
            return IndexActionResult(
                action="collect", message=f"Index {index_id} collected."
            )

        code, payload = await client.delete_index_collection(index_id)
        ensure_ok(code, payload)
        return IndexActionResult(
            action="uncollect", message=f"Index {index_id} uncollected."
        )
