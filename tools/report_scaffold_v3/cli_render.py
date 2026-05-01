"""Rendering and formatting helpers for CLI output.

These functions convert structured report dicts into human-readable
Markdown summaries for terminal display.  They were extracted from
cli.py to reduce that module's density without changing any command
behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Import / build / assembly summaries
# ---------------------------------------------------------------------------


def render_import_summary(
    inventory: dict,
    *,
    target_role: str,
    format_authority_docx: Optional[Path],
) -> str:
    summary = inventory["summary"]
    lines = [
        "# Baseline Import Summary",
        "",
        f"- Source docx: `{inventory['source_docx']}`",
        f"- Target role: `{target_role}`",
        f"- Formatting authority: `{format_authority_docx}`"
        if format_authority_docx is not None
        else "- Formatting authority: `[none]`",
        f"- Paragraphs: {summary['paragraph_count']}",
        f"- Headings: {summary['heading_count']}",
        f"- Figures: {summary['figure_count']}",
        f"- Image relationships: {summary['image_relationship_count']}",
        f"- Image paragraphs: {summary['image_paragraph_count']}",
        f"- Sections: {summary['section_count']}",
        f"- Appendix headings: {summary['appendix_heading_count']}",
        f"- Appendix file references: {summary['appendix_file_reference_count']}",
        "",
        "## Top Headings",
        "",
    ]
    for heading in inventory["headings"][:15]:
        lines.append(f"- L{heading['level']} `{heading['section_id']}`: {heading['text']}")
    return "\n".join(lines)


def render_build_summary(result: dict) -> str:
    lines = [
        "# Build Summary",
        "",
        f"- Document ID: `{result['document_id']}`",
        f"- Template docx: `{result['template_docx']}`",
        f"- Output docx: `{result['output_docx']}`",
        f"- Blocks: {result['block_count']}",
        f"- Rendered paragraphs: {result['paragraph_count']}",
        f"- Image blocks: {result['image_count']}",
    ]
    return "\n".join(lines)


def render_section_assembly_summary(build_source: dict, *, output_path: Path) -> str:
    lines = [
        "# Section Assembly Summary",
        "",
        f"- Document ID: `{build_source['document_id']}`",
        f"- Output name: `{build_source['output_name']}`",
        f"- Block count: {len(build_source['blocks'])}",
        f"- Generated build source: `{output_path}`",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Audit summaries
# ---------------------------------------------------------------------------


def render_font_audit_summary(report: dict) -> str:
    lines = [
        "# Font Audit Summary",
        "",
        f"- Source docx: `{report['source_docx']}`",
        f"- Expected font: `{report['expected_font']}`",
        f"- Total runs scanned: {report['total_runs_scanned']}",
        f"- Explicit expected-font runs: {report['explicit_expected_font_runs']}",
        f"- Inherited-font runs: {report['inherited_font_runs']}",
        f"- Explicit other-font runs: {report['explicit_other_font_runs']}",
    ]
    return "\n".join(lines)


def render_outline_audit_summary(report: dict) -> str:
    lines = [
        "# Outline Audit Summary",
        "",
        f"- Source docx: `{report['source_docx']}`",
        f"- Heading count: {report['heading_count']}",
        f"- Appendix heading count: {report['appendix_heading_count']}",
        f"- Heading levels: {report['heading_level_counts']}",
        f"- Duplicate heading texts: {len(report['duplicate_heading_texts'])}",
    ]
    return "\n".join(lines)


def render_candidate_audit_summary(report: dict) -> str:
    lines = [
        "# Candidate Audit Summary",
        "",
        f"- Source docx: `{report['source_docx']}`",
        f"- Expected paragraph count: {report['expected_paragraph_count']}",
        f"- Actual paragraph count: {report['actual_paragraph_count']}",
        f"- Expected heading count: {report['expected_heading_count']}",
        f"- Actual heading count: {report['actual_heading_count']}",
        f"- Expected image count: {report['expected_image_count']}",
        f"- Actual figure count: {report['actual_figure_count']}",
        f"- Expected snippet count: {report['expected_snippet_count']}",
        f"- Actual snippet count: {report['actual_snippet_count']}",
        f"- Finding count: {len(report['findings'])}",
    ]
    return "\n".join(lines)


def render_snippet_audit_summary(report: dict) -> str:
    lines = [
        "# Snippet Audit Summary",
        "",
        f"- Source manifest: `{report['source_manifest']}`",
        f"- Snippets checked: {report['snippets_checked']}",
        f"- Findings: {len(report['findings'])}",
        f"- Extracted entries: {len(report['entries'])}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OfficeX sandbox / task / workspace
# ---------------------------------------------------------------------------


def render_officex_sandbox_created(run_id: str, sandbox_root: Path) -> str:
    return f"Created OfficeX sandbox `{run_id}` at {sandbox_root}"


def render_officex_task_run(report: dict) -> str:
    return (
        "Ran OfficeX docx MVP task "
        f"`{report['run_id']}` with candidate {report['candidate_docx']} "
        f"and validation {report['validation_error_count']} error(s) / "
        f"{report['validation_warning_count']} warning(s)."
    )


def render_officex_workspace_created(report: dict) -> str:
    return (
        "Created OfficeX workspace "
        f"`{report['workspace_id']}` at {report['root_path']} "
        f"with sandbox root {report['sandboxes_dir']}."
    )


def render_officex_task_packet(report: dict) -> str:
    lines = [
        "# OfficeX Task Packet Inspection",
        "",
        f"- Task packet ID: `{report['task_packet_id']}`",
        f"- Goal: {report['goal']}",
        f"- Task family: `{report['task_family']}`",
        f"- Active workspace: `{report['active_workspace']}`",
        f"- Approval mode: `{report['approval_mode']}`",
        f"- Publish gate: `{report['publish_gate']}`",
    ]
    if report["allowed_surfaces"]:
        lines.extend(["", "## Allowed Surfaces", ""])
        for item in report["allowed_surfaces"]:
            lines.append(f"- `{item}`")
    if report["acceptance_gates"]:
        lines.extend(["", "## Acceptance Gates", ""])
        for item in report["acceptance_gates"]:
            lines.append(f"- {item}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OfficeX provider / prompt / agent
# ---------------------------------------------------------------------------


def render_officex_provider_list(report: dict) -> str:
    lines = ["# OfficeX Providers", ""]
    for provider in report["providers"]:
        lines.append(
            "- "
            f"`{provider['provider_id']}` "
            f"({provider['display_name']}) "
            f"status: `{provider['status']}` "
            f"default model: `{provider['default_model_id']}`"
        )
    return "\n".join(lines)


def render_officex_provider_binding(report: dict, *, include_prompt: bool) -> str:
    lines = [
        "# OfficeX Provider Binding",
        "",
        f"- Provider: `{report['provider_id']}` ({report['provider_display_name']})",
        f"- Adapter kind: `{report['adapter_kind']}`",
        f"- Status: `{report['status']}`",
        f"- Auth scheme: `{report['auth_scheme']}`",
        f"- Model: `{report['model_id']}`",
        f"- Role: `{report['role']}`",
        f"- Include cognition: `{report['include_cognition']}`",
        f"- Structured output: `{report['supports_structured_output']}`",
        f"- Tool calls: `{report['supports_tool_calls']}`",
        f"- Image generation: `{report['supports_image_generation']}`",
        f"- Long context: `{report['supports_long_context']}`",
        f"- Latency class: `{report['latency_class']}`",
    ]
    if report["prompt_manifest"]:
        lines.extend(["", "## Prompt Manifest", ""])
        for entry in report["prompt_manifest"]:
            lines.append(
                f"- `{entry['layer']}` -> `{entry['ref']}` (`{entry['prompt_id']}`)"
            )
    if report["resolved_rule_refs"]:
        lines.extend(["", "## Resolved Prompt Refs", ""])
        for entry in report["resolved_rule_refs"]:
            lines.append(
                "- "
                f"`{entry['section_title']}` "
                f"from `{entry['ref']}` "
                f"(sha256 `{entry['content_sha256'][:12]}`...)"
            )
    if report["config_fields"]:
        lines.extend(["", "## Config Fields", ""])
        for field_name in report["config_fields"]:
            lines.append(f"- `{field_name}`")
    if report["notes"]:
        lines.extend(["", "## Notes", ""])
        for note in report["notes"]:
            lines.append(f"- {note}")
    if include_prompt:
        lines.extend(["", "## Compiled Prompt Debug", "", report["compiled_prompt_debug"].rstrip()])
    return "\n".join(lines)


def render_officex_provider_request(report: dict) -> str:
    missing_fields = [
        field_name
        for field_name in report["required_config_fields"]
        if field_name not in set(report["provided_config_fields"])
    ]
    lines = [
        "# OfficeX Provider Request Envelope",
        "",
        f"- Envelope: `{report['envelope_id']}`",
        f"- Provider: `{report['provider_id']}`",
        f"- Model: `{report['model_id']}`",
        f"- Adapter kind: `{report['adapter_kind']}`",
        f"- Dispatch mode: `{report['dispatch_mode']}`",
        f"- Role: `{report['role']}`",
        f"- Include cognition: `{report['include_cognition']}`",
        f"- Task packet: `{report['task_packet_id']}`",
        f"- Task family: `{report['task_family']}`",
        f"- Approval mode: `{report['approval_mode']}`",
        f"- Response contract: `{report['response_contract_kind']}`",
        f"- Prompt layers: {len(report['prompt_manifest'])}",
        "",
        "## Config Coverage",
        "",
        f"- Required fields: {', '.join(report['required_config_fields']) if report['required_config_fields'] else '[none]'}",
        f"- Provided fields: {', '.join(report['provided_config_fields']) if report['provided_config_fields'] else '[none]'}",
        f"- Missing required fields: {', '.join(missing_fields) if missing_fields else 'none'}",
    ]
    if report["prompt_manifest"]:
        lines.extend(["", "## Prompt Manifest", ""])
        for entry in report["prompt_manifest"]:
            lines.append(
                f"- `{entry['layer']}` -> `{entry['ref']}` (`{entry['prompt_id']}`)"
            )
    return "\n".join(lines)


def render_officex_agent_list(report: dict) -> str:
    lines = ["# OfficeX Agents", ""]
    for agent in report["agents"]:
        lines.append(
            "- "
            f"`{agent['agent_id']}` "
            f"({agent['display_name']}) "
            f"status: `{agent['status']}` "
            f"role: `{agent['runtime_role']}`"
        )
    return "\n".join(lines)


def render_officex_agent_show(report: dict) -> str:
    lines = [
        "# OfficeX Agent",
        "",
        f"- Agent: `{report['agent_id']}` ({report['display_name']})",
        f"- Runtime role: `{report['runtime_role']}`",
        f"- Status: `{report['status']}`",
    ]
    if report["prompt_roles"]:
        lines.extend(["", "## Prompt Roles", ""])
        for role in report["prompt_roles"]:
            lines.append(f"- `{role}`")
    if report["domain_pack_candidates"]:
        lines.extend(["", "## Domain Pack Candidates", ""])
        for item in report["domain_pack_candidates"]:
            lines.append(f"- `{item}`")
    if report["review_pack_candidates"]:
        lines.extend(["", "## Review Pack Candidates", ""])
        for item in report["review_pack_candidates"]:
            lines.append(f"- `{item}`")
    if report["owned_capabilities"]:
        lines.extend(["", "## Owned Capabilities", ""])
        for item in report["owned_capabilities"]:
            lines.append(f"- {item}")
    if report["notes"]:
        lines.extend(["", "## Notes", ""])
        for note in report["notes"]:
            lines.append(f"- {note}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OfficeX doctor / render-boundary
# ---------------------------------------------------------------------------


def render_officex_doctor_report(report: dict) -> str:
    lines = [
        "# OfficeX Doctor",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Platform: `{report['platform']}`",
        f"- Workspace root: `{report['workspace_root']}`",
        f"- Sandbox root: `{report['sandbox_root']}`",
        f"- Next action: {report['recommended_next_action']}",
        "",
    ]
    for check in report["checks"]:
        lines.extend(
            [
                f"## {check['title']}",
                "",
                f"- Status: `{check['status']}`",
                f"- Summary: {check['summary']}",
            ]
        )
        if check["detail_lines"]:
            lines.append("- Details:")
            lines.extend([f"  - {line}" for line in check["detail_lines"]])
        if check["remediation"]:
            lines.append("- Remediation:")
            lines.extend([f"  - {line}" for line in check["remediation"]])
        lines.append("")
    return "\n".join(lines)


def render_officex_render_boundary_report(report: dict) -> str:
    lines = [
        "# OfficeX Render Boundary",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Renderer: `{report['renderer_profile']['display_name']}`",
        f"- Renderer detected: `{report['renderer_profile']['detected']}`",
        f"- Renderer version: `{report['renderer_profile']['version'] or '[unknown]'}`",
        "",
        "## Scenarios",
        "",
    ]
    if not report["scenarios"]:
        lines.append("- No executable scenarios were run.")
    else:
        for scenario in report["scenarios"]:
            lines.append(
                "- "
                f"`{scenario['scenario_id']}` "
                f"/ `{scenario['document_length']}` "
                f"/ `{scenario['operation_profile']}` "
                f"/ `{scenario['status']}`"
            )
    if report["residual_risk_notes"]:
        lines.extend(["", "## Residual Risks", ""])
        for note in report["residual_risk_notes"]:
            lines.append(f"- {note}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OfficeX trace / patch / review / pipeline / publication
# ---------------------------------------------------------------------------


def render_officex_trace_checkpoint(report: dict) -> str:
    return (
        "Created OfficeX trace checkpoint "
        f"`{report['checkpoint_id']}` at {report['checkpoint_path']}."
    )


def render_officex_patch_bridge_report(report: dict) -> str:
    lines = [
        "# OfficeX Patch Bridge Report",
        "",
        f"- Patch bundle: `{report['patch_bundle_id']}`",
        f"- Target document: `{report['target_document_id']}`",
        f"- Candidate: `{report['candidate_path']}`",
        f"- Anchor snapshot: `{report['anchor_snapshot_path']}`",
        f"- Patch bridge spec: `{report['patch_spec_path']}`",
        f"- Patch bridge execution report: `{report['execution_report_path']}`",
        f"- Dry run: `{report['dry_run']}`",
        f"- Status: `{report['status']}`",
        f"- Operation count: {report['operation_count']}",
        f"- Applied operations: {report['applied_operation_count']}",
        f"- Rejected operations: {report['rejected_operation_count']}",
    ]
    if report["backup_path"]:
        lines.append(f"- Backup path: `{report['backup_path']}`")
    if report["output_candidate_hash"]:
        lines.append(f"- Output candidate hash: `{report['output_candidate_hash']}`")
    if report["failure_reason"]:
        lines.append(f"- Failure reason: {report['failure_reason']}")
    return "\n".join(lines)


def render_officex_review_ledger(report: dict, *, output_path: Path) -> str:
    return (
        "Built OfficeX review ledger "
        f"`{report['review_id']}` with {len(report['findings'])} finding(s) at {output_path}."
    )


def render_officex_anchor_prep_report(report: dict) -> str:
    return (
        "Extracted OfficeX live anchors for review "
        f"`{report['review_id']}` into {report['output_dir']} "
        f"with {report['anchor_count']} anchor(s) and {report['finding_count']} finding(s)."
    )


def render_section_pipeline_summary(report: dict) -> str:
    lines = [
        "# Section Pipeline Summary",
        "",
        f"- Build source: `{report['build_source_path']}`",
        f"- Output docx: `{report['output_docx']}`",
        f"- Candidate audit: `{report['candidate_audit_path']}`",
        f"- Validation report: `{report['validation_report_path']}`",
        f"- Candidate errors: {report['candidate_error_count']}",
        f"- Candidate warnings: {report['candidate_warning_count']}",
        f"- Validation errors: {report['validation_error_count']}",
        f"- Validation warnings: {report['validation_warning_count']}",
    ]
    return "\n".join(lines)


def render_published_run_summary(report: dict) -> str:
    lines = [
        "# Published Run Summary",
        "",
        f"- Published id: `{report['published_id']}`",
        f"- Published at (UTC): `{report['published_at_utc']}`",
        f"- Run dir: `{report['run_dir']}`",
        f"- Canonical root: `{report['canonical_root']}`",
        f"- Output docx: `{report['output_docx']}`",
        f"- Candidate errors/warnings: {report['candidate_error_count']}/{report['candidate_warning_count']}",
        f"- Validation errors/warnings: {report['validation_error_count']}/{report['validation_warning_count']}",
    ]
    return "\n".join(lines)


def render_trace_catalog_summary(report: dict) -> str:
    lines = [
        "# Trace Catalog Summary",
        "",
        f"- Trace dir: `{report['trace_dir']}`",
        f"- Checkpoint count: {report['checkpoint_count']}",
        f"- Latest checkpoint: `{report['latest_checkpoint_id']}`",
        f"- Missing numbers: {', '.join(str(value) for value in report['missing_numbers'])}"
        if report["missing_numbers"]
        else "- Missing numbers: none",
    ]
    return "\n".join(lines)
