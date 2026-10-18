from __future__ import annotations

import asyncio
import json

from tools.report_scaffold_v3 import mcp_server


def _call(name: str, arguments: dict) -> dict:
    contents = asyncio.run(mcp_server.call_tool(name, arguments))
    assert len(contents) == 1
    return json.loads(contents[0].text)


def test_mcp_server_lists_officex_tools():
    tools = asyncio.run(mcp_server.list_tools())
    names = {tool.name for tool in tools}

    assert {
        "officex_generate",
        "officex_generate_long",
        "officex_edit",
        "officex_audit_visual",
        "officex_diff",
        "officex_profile_list",
        "officex_doctor",
    } <= names
    for tool in tools:
        assert tool.description
        assert tool.inputSchema["type"] == "object"


def test_mcp_profile_list_returns_json_payload():
    payload = _call("officex_profile_list", {})

    assert payload["active"]
    assert {profile["profile_id"] for profile in payload["profiles"]} >= {"a4_academic", "letter_business"}


def test_mcp_unknown_tool_returns_error_payload():
    payload = _call("officex_nope", {})

    assert payload == {"error": "Unknown tool: officex_nope"}
