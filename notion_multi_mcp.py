"""notion-multi-mcp — MCP Server for multiple Notion accounts."""

# ── Import ──────────────────────────────────────────────────────
import json
import os
import sys

import httpx
from mcp.server.fastmcp import FastMCP

from notion_client import Client

# ── Parse NOTION_ACCOUNTS env var ───────────────────────────────
# Format: "prefix1:ntn_key1,prefix2:ntn_key2,prefix3:ntn_key3"
accounts_raw = os.environ.get("NOTION_ACCOUNTS", "")

if not accounts_raw:
    print(
        "Error: NOTION_ACCOUNTS is not set.\n"
        "Format: NOTION_ACCOUNTS=\"work:ntn_xxx,personal:ntn_yyy\"\n"
        "See README for details.",
        file=sys.stderr,
    )
    sys.exit(1)

accounts: list[tuple[str, str]] = []
for pair in accounts_raw.split(","):
    pair = pair.strip()
    if ":" not in pair:
        print(
            f"Error: invalid account format '{pair}'. Expected 'prefix:api_key'.",
            file=sys.stderr,
        )
        sys.exit(1)
    prefix, api_key = pair.split(":", 1)
    prefix = prefix.strip()
    api_key = api_key.strip()
    if not prefix or not api_key:
        print(
            f"Error: empty prefix or api_key in '{pair}'.",
            file=sys.stderr,
        )
        sys.exit(1)
    accounts.append((prefix, api_key))

# ── FastMCP Server ──────────────────────────────────────────────
mcp = FastMCP("notion-multi-mcp")


# ── Helper ─────────────────────────────────────────────────────
def _parse_json(value: str | dict | list) -> dict | list:
    """Accept a JSON string *or* an already-parsed object (dict/list).

    Some MCP clients (e.g. Claude Code) may send dict/list instead of a
    JSON string for optional parameters whose schema is ``anyOf: [string, null]``.
    This helper normalises both cases so tool handlers just work.
    """
    if isinstance(value, (dict, list)):
        return value
    return json.loads(value)


# ── register_tools() factory ────────────────────────────────────
def register_tools(prefix: str, client: Client, api_key: str) -> None:
    """Register all 22 Notion tools for one account with the given prefix."""

    def _raw_request(method: str, path: str, body: dict | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2025-02-19",
            "Content-Type": "application/json",
        }
        url = f"https://api.notion.com/v1/{path}"
        if method == "GET":
            resp = httpx.get(url, headers=headers, timeout=30.0)
        elif method == "POST":
            resp = httpx.post(url, headers=headers, json=body or {}, timeout=30.0)
        elif method == "PATCH":
            resp = httpx.patch(url, headers=headers, json=body or {}, timeout=30.0)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        resp.raise_for_status()
        return resp.json()

    # ── 1: search ────────────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_search", description=f"[{prefix}] Search pages and databases")
    def search(
        query: str = "",
        filter_json: str | dict | None = None,
        sort_json: str | dict | None = None,
        start_cursor: str | None = None,
        page_size: int = 100,
    ) -> str:
        try:
            kwargs: dict = {"query": query, "page_size": page_size}
            if filter_json is not None:
                kwargs["filter"] = _parse_json(filter_json)
            if sort_json is not None:
                kwargs["sort"] = _parse_json(sort_json)
            if start_cursor is not None:
                kwargs["start_cursor"] = start_cursor
            return json.dumps(client.search(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 2: query_database ────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_query_database", description=f"[{prefix}] Query database contents (use data_source_id, not database_id)")
    def query_database(
        data_source_id: str,
        filter_json: str | dict | None = None,
        sorts_json: str | list | None = None,
        start_cursor: str | None = None,
        page_size: int = 100,
    ) -> str:
        try:
            kwargs: dict = {"data_source_id": data_source_id, "page_size": page_size}
            if filter_json is not None:
                kwargs["filter"] = _parse_json(filter_json)
            if sorts_json is not None:
                kwargs["sorts"] = _parse_json(sorts_json)
            if start_cursor is not None:
                kwargs["start_cursor"] = start_cursor
            return json.dumps(client.data_sources.query(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 3: create_page ───────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_create_page", description=f"[{prefix}] Create a new page")
    def create_page(
        parent_json: str | dict,
        properties_json: str | dict,
        children_json: str | list | None = None,
        icon_json: str | dict | None = None,
        cover_json: str | dict | None = None,
    ) -> str:
        try:
            kwargs: dict = {
                "parent": _parse_json(parent_json),
                "properties": _parse_json(properties_json),
            }
            if children_json is not None:
                kwargs["children"] = _parse_json(children_json)
            if icon_json is not None:
                kwargs["icon"] = _parse_json(icon_json)
            if cover_json is not None:
                kwargs["cover"] = _parse_json(cover_json)
            return json.dumps(client.pages.create(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 4: retrieve_page ─────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_retrieve_page", description=f"[{prefix}] Get page information")
    def retrieve_page(page_id: str) -> str:
        try:
            return json.dumps(client.pages.retrieve(page_id=page_id), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 5: update_page ───────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_update_page", description=f"[{prefix}] Update page properties")
    def update_page(
        page_id: str,
        properties_json: str | dict | None = None,
        icon_json: str | dict | None = None,
        cover_json: str | dict | None = None,
        archived: bool | None = None,
    ) -> str:
        try:
            kwargs: dict = {"page_id": page_id}
            if properties_json is not None:
                kwargs["properties"] = _parse_json(properties_json)
            if icon_json is not None:
                kwargs["icon"] = _parse_json(icon_json)
            if cover_json is not None:
                kwargs["cover"] = _parse_json(cover_json)
            if archived is not None:
                kwargs["archived"] = archived
            return json.dumps(client.pages.update(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 6: retrieve_page_property ────────────────────────────────
    @mcp.tool(name=f"{prefix}_retrieve_page_property", description=f"[{prefix}] Get a specific page property")
    def retrieve_page_property(
        page_id: str,
        property_id: str,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> str:
        try:
            kwargs: dict = {"page_id": page_id, "property_id": property_id}
            if start_cursor is not None:
                kwargs["start_cursor"] = start_cursor
            if page_size is not None:
                kwargs["page_size"] = page_size
            return json.dumps(client.pages.properties.retrieve(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 7: move_page ─────────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_move_page", description=f"[{prefix}] Move a page to a new parent")
    def move_page(page_id: str, new_parent_json: str | dict) -> str:
        try:
            return json.dumps(
                _raw_request("POST", f"pages/{page_id}/move", body={"parent": _parse_json(new_parent_json)}),
                ensure_ascii=False,
            )
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 8: retrieve_block ────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_retrieve_block", description=f"[{prefix}] Get block information")
    def retrieve_block(block_id: str) -> str:
        try:
            return json.dumps(client.blocks.retrieve(block_id=block_id), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 9: update_block ──────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_update_block", description=f"[{prefix}] Update a block")
    def update_block(block_id: str, block_json: str | dict) -> str:
        try:
            return json.dumps(client.blocks.update(block_id=block_id, **_parse_json(block_json)), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 10: delete_block ─────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_delete_block", description=f"[{prefix}] Delete a block")
    def delete_block(block_id: str) -> str:
        try:
            return json.dumps(client.blocks.delete(block_id=block_id), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 11: get_block_children ───────────────────────────────────
    @mcp.tool(name=f"{prefix}_get_block_children", description=f"[{prefix}] List child blocks")
    def get_block_children(
        block_id: str,
        start_cursor: str | None = None,
        page_size: int = 100,
    ) -> str:
        try:
            kwargs: dict = {"block_id": block_id, "page_size": page_size}
            if start_cursor is not None:
                kwargs["start_cursor"] = start_cursor
            return json.dumps(client.blocks.children.list(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 12: append_block_children ────────────────────────────────
    @mcp.tool(name=f"{prefix}_append_block_children", description=f"[{prefix}] Append child blocks")
    def append_block_children(block_id: str, children_json: str | list) -> str:
        try:
            return json.dumps(
                client.blocks.children.append(block_id=block_id, children=_parse_json(children_json)),
                ensure_ascii=False,
            )
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 13: retrieve_database ────────────────────────────────────
    @mcp.tool(name=f"{prefix}_retrieve_database", description=f"[{prefix}] Get database schema")
    def retrieve_database(database_id: str) -> str:
        try:
            return json.dumps(client.databases.retrieve(database_id=database_id), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 14: create_database ──────────────────────────────────────
    @mcp.tool(name=f"{prefix}_create_database", description=f"[{prefix}] Create a new database")
    def create_database(
        parent_json: str | dict,
        title_json: str | list,
        properties_json: str | dict,
        icon_json: str | dict | None = None,
        cover_json: str | dict | None = None,
    ) -> str:
        try:
            kwargs: dict = {
                "parent": _parse_json(parent_json),
                "title": _parse_json(title_json),
                "properties": _parse_json(properties_json),
            }
            if icon_json is not None:
                kwargs["icon"] = _parse_json(icon_json)
            if cover_json is not None:
                kwargs["cover"] = _parse_json(cover_json)
            return json.dumps(client.databases.create(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 15: update_database ──────────────────────────────────────
    @mcp.tool(name=f"{prefix}_update_database", description=f"[{prefix}] Update database properties")
    def update_database(
        database_id: str,
        title_json: str | list | None = None,
        properties_json: str | dict | None = None,
        icon_json: str | dict | None = None,
        cover_json: str | dict | None = None,
    ) -> str:
        try:
            kwargs: dict = {"database_id": database_id}
            if title_json is not None:
                kwargs["title"] = _parse_json(title_json)
            if properties_json is not None:
                kwargs["properties"] = _parse_json(properties_json)
            if icon_json is not None:
                kwargs["icon"] = _parse_json(icon_json)
            if cover_json is not None:
                kwargs["cover"] = _parse_json(cover_json)
            return json.dumps(client.databases.update(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 16: query_data_source ────────────────────────────────────
    @mcp.tool(name=f"{prefix}_query_data_source", description=f"[{prefix}] Query a data source")
    def query_data_source(
        data_source_id: str,
        filter_json: str | dict | None = None,
        sorts_json: str | list | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> str:
        try:
            kwargs: dict = {"data_source_id": data_source_id}
            if filter_json is not None:
                kwargs["filter"] = _parse_json(filter_json)
            if sorts_json is not None:
                kwargs["sorts"] = _parse_json(sorts_json)
            if start_cursor is not None:
                kwargs["start_cursor"] = start_cursor
            if page_size is not None:
                kwargs["page_size"] = page_size
            return json.dumps(client.data_sources.query(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 17: retrieve_data_source ─────────────────────────────────
    @mcp.tool(name=f"{prefix}_retrieve_data_source", description=f"[{prefix}] Get data source info")
    def retrieve_data_source(data_source_id: str) -> str:
        try:
            return json.dumps(client.data_sources.retrieve(data_source_id=data_source_id), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 18: list_data_source_templates ───────────────────────────
    @mcp.tool(name=f"{prefix}_list_data_source_templates", description=f"[{prefix}] List data source templates")
    def list_data_source_templates(data_source_id: str) -> str:
        try:
            return json.dumps(client.data_sources.list_templates(data_source_id=data_source_id), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 19: update_data_source ───────────────────────────────────
    @mcp.tool(name=f"{prefix}_update_data_source", description=f"[{prefix}] Update a data source")
    def update_data_source(data_source_id: str, data_json: str | dict) -> str:
        try:
            return json.dumps(
                client.data_sources.update(data_source_id=data_source_id, **_parse_json(data_json)),
                ensure_ascii=False,
            )
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 20: create_comment ───────────────────────────────────────
    @mcp.tool(name=f"{prefix}_create_comment", description=f"[{prefix}] Create a comment")
    def create_comment(
        rich_text_json: str | list,
        parent_json: str | dict | None = None,
        discussion_id: str | None = None,
    ) -> str:
        try:
            kwargs: dict = {"rich_text": _parse_json(rich_text_json)}
            if parent_json is not None:
                kwargs["parent"] = _parse_json(parent_json)
            if discussion_id is not None:
                kwargs["discussion_id"] = discussion_id
            return json.dumps(client.comments.create(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 21: retrieve_comments ────────────────────────────────────
    @mcp.tool(name=f"{prefix}_retrieve_comments", description=f"[{prefix}] List comments")
    def retrieve_comments(
        block_id: str,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> str:
        try:
            kwargs: dict = {"block_id": block_id}
            if start_cursor is not None:
                kwargs["start_cursor"] = start_cursor
            if page_size is not None:
                kwargs["page_size"] = page_size
            return json.dumps(client.comments.list(**kwargs), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ── 22: get_self ─────────────────────────────────────────────
    @mcp.tool(name=f"{prefix}_get_self", description=f"[{prefix}] Get bot user info")
    def get_self() -> str:
        try:
            return json.dumps(client.users.me(), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── Register tools for each account ────────────────────────────
for _prefix, _api_key in accounts:
    _client = Client(auth=_api_key)
    register_tools(_prefix, _client, _api_key)

print(
    f"notion-multi-mcp: loaded {len(accounts)} account(s) "
    f"({', '.join(p for p, _ in accounts)}) — {len(accounts) * 22} tools ready.",
    file=sys.stderr,
)


# ── Entry point ─────────────────────────────────────────────────
def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
