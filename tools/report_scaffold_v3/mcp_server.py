"""OfficeX MCP Server: expose document operations as MCP tools.

Run with: officex serve
Or: python -m tools.report_scaffold_v3.mcp_server

Exposes OfficeX capabilities as MCP tools that Claude Desktop,
Cursor, and other MCP clients can discover and invoke.
"""

from __future__ import annotations

import json
import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("officex")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="officex_generate",
            description="Generate a Word document from a prompt. Returns the path to the generated .docx and validation results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "What document to create"},
                    "model": {"type": "string", "description": "AI model to use (e.g. qwen-plus)", "default": "qwen-plus"},
                    "profile": {"type": "string", "description": "Document profile (e.g. a4_academic, letter_business)", "default": ""},
                    "output_dir": {"type": "string", "description": "Output directory path", "default": ""},
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="officex_generate_long",
            description="Generate a long multi-section document from a YAML outline file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "outline_path": {"type": "string", "description": "Path to YAML outline file"},
                    "model": {"type": "string", "description": "AI model to use", "default": "qwen-plus"},
                    "output_dir": {"type": "string", "description": "Output directory path", "default": ""},
                },
                "required": ["outline_path"],
            },
        ),
        Tool(
            name="officex_edit",
            description="Edit an existing Word document based on instructions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "docx_path": {"type": "string", "description": "Path to the docx file to edit"},
                    "instruction": {"type": "string", "description": "What to change"},
                    "model": {"type": "string", "description": "AI model to use", "default": "qwen-plus"},
                },
                "required": ["docx_path", "instruction"],
            },
        ),
        Tool(
            name="officex_audit_visual",
            description="Render a Word document to PNG pages and run visual quality checks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "docx_path": {"type": "string", "description": "Path to the docx file to audit"},
                    "output_dir": {"type": "string", "description": "Output directory for PNG pages"},
                },
                "required": ["docx_path", "output_dir"],
            },
        ),
        Tool(
            name="officex_diff",
            description="Visually compare two Word documents page by page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "docx_a": {"type": "string", "description": "Path to first docx"},
                    "docx_b": {"type": "string", "description": "Path to second docx"},
                    "output_dir": {"type": "string", "description": "Output directory for diff images"},
                },
                "required": ["docx_a", "docx_b", "output_dir"],
            },
        ),
        Tool(
            name="officex_profile_list",
            description="List available document profiles with their configurations.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="officex_doctor",
            description="Check environment readiness (Python, LibreOffice, dependencies, API key).",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result = await asyncio.to_thread(_call_tool_sync, name, arguments)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


def _call_tool_sync(name: str, arguments: dict) -> dict:
    """Synchronous tool dispatch."""
    if name == "officex_generate":
        from .generate_runtime import run_generate
        if arguments.get("profile"):
            from .profile_runtime import activate_profile
            activate_profile(arguments["profile"])
        report = run_generate(
            prompt=arguments["prompt"],
            model_id=arguments.get("model"),
            output_dir=Path(arguments["output_dir"]) if arguments.get("output_dir") else None,
        )
        return report.to_dict()

    if name == "officex_generate_long":
        from .long_generate_runtime import run_long_generate
        report = run_long_generate(
            outline_path=Path(arguments["outline_path"]),
            model_id=arguments.get("model"),
            output_dir=Path(arguments["output_dir"]) if arguments.get("output_dir") else None,
        )
        return report.to_dict()

    if name == "officex_edit":
        from .edit_runtime import run_edit
        report = run_edit(
            docx_path=Path(arguments["docx_path"]),
            instruction=arguments["instruction"],
            model_id=arguments.get("model"),
        )
        return report.to_dict()

    if name == "officex_audit_visual":
        from .visual_audit import render_docx_to_png
        from .visual_audit_checks import run_visual_checks
        report = render_docx_to_png(
            Path(arguments["docx_path"]),
            Path(arguments["output_dir"]),
        )
        findings = []
        if report.status == "pass":
            findings = run_visual_checks(report.png_paths)
        result = report.model_dump(mode="json")
        result["visual_findings"] = [f.model_dump(mode="json") for f in findings]
        return result

    if name == "officex_diff":
        from .diff_runtime import run_diff
        report = run_diff(
            docx_a=Path(arguments["docx_a"]),
            docx_b=Path(arguments["docx_b"]),
            output_dir=Path(arguments["output_dir"]),
        )
        return report.to_dict()

    if name == "officex_profile_list":
        from .profile_runtime import list_profiles, get_active_profile_id
        return {"active": get_active_profile_id(), "profiles": list_profiles()}

    if name == "officex_doctor":
        from .doctor_runtime import build_doctor_report
        from .paths import WORKSPACES_DIR, SANDBOXES_DIR, DEFAULT_OFFICEX_DESKTOP_SHELL_DIR
        report = build_doctor_report(
            workspace_root=WORKSPACES_DIR / "default",
            sandbox_root=SANDBOXES_DIR,
            desktop_shell_dir=DEFAULT_OFFICEX_DESKTOP_SHELL_DIR,
        )
        return report.model_dump(mode="json")

    return {"error": f"Unknown tool: {name}"}


async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
