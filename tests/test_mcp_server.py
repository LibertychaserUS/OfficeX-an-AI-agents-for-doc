from __future__ import annotations

import asyncio
import json

from mcp import types

from tools.report_scaffold_v3 import mcp_server


def _call(name: str, arguments: dict) -> types.CallToolResult:
    """Dispatch through the server's registered handler, as an MCP client would."""
    handler = mcp_server.server.request_handlers[types.CallToolRequest]
    request = types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(name=name, arguments=arguments),
    )
    return asyncio.run(handler(request)).root


def _payload(result: types.CallToolResult) -> dict:
    assert result.isError is False, result.content[0].text
    return json.loads(result.content[0].text)


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
    payload = _payload(_call("officex_profile_list", {}))

    assert payload["active"]
    assert {profile["profile_id"] for profile in payload["profiles"]} >= {"a4_academic", "letter_business"}


def test_mcp_unknown_tool_returns_error_payload():
    payload = _payload(_call("officex_nope", {}))

    assert payload == {"error": "Unknown tool: officex_nope"}


def test_mcp_audit_visual_reports_missing_docx_as_error(tmp_path):
    result = _call(
        "officex_audit_visual",
        {"docx_path": str(tmp_path / "missing.docx"), "output_dir": str(tmp_path / "out")},
    )

    assert result.isError is True
    assert "docx_path: file not found" in result.content[0].text


def test_mcp_diff_reports_missing_docx_as_error(tmp_path):
    existing = tmp_path / "a.docx"
    existing.write_bytes(b"")

    result = _call(
        "officex_diff",
        {"docx_a": str(existing), "docx_b": str(tmp_path / "b.docx"), "output_dir": str(tmp_path / "out")},
    )

    assert result.isError is True
    assert "docx_b: file not found" in result.content[0].text
