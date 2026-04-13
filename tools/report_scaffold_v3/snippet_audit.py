from __future__ import annotations

from pathlib import Path

from .manifest_loader import load_snippets_manifest
from .models import SnippetAuditEntry, SnippetAuditFinding, SnippetAuditReport
from .snippet_compiler import SnippetCompilationError, extract_snippet_text, resolve_snippet_source_path


def build_snippet_audit(
    manifest_path: Path,
) -> SnippetAuditReport:
    manifest = load_snippets_manifest(manifest_path)
    entries: list[SnippetAuditEntry] = []
    findings: list[SnippetAuditFinding] = []

    for snippet in manifest.managed_snippets:
        try:
            source_path = resolve_snippet_source_path(snippet.source_path)
            extracted_text = extract_snippet_text(snippet)
            line_span = None
            if snippet.extract_mode == "line_range":
                line_span = f"{snippet.start_line}-{snippet.end_line}"
            entries.append(
                SnippetAuditEntry(
                    snippet_id=snippet.snippet_id,
                    source_path=source_path,
                    target_section_id=snippet.target_section_id,
                    language=snippet.language,
                    line_span=line_span,
                    extracted_line_count=len(extracted_text.splitlines()),
                    preview=extracted_text.splitlines()[0][:120],
                )
            )
        except SnippetCompilationError as exc:
            findings.append(
                SnippetAuditFinding(
                    severity="error",
                    code="snippet-extraction-failed",
                    message=str(exc),
                )
            )

    return SnippetAuditReport(
        source_manifest=manifest_path,
        snippets_checked=len(manifest.managed_snippets),
        findings=findings,
        entries=entries,
    )


def render_snippet_audit_markdown(report: SnippetAuditReport) -> str:
    lines = [
        "# Snippet Audit Report",
        "",
        f"- Source manifest: `{report.source_manifest}`",
        f"- Snippets checked: {report.snippets_checked}",
        f"- Findings: {len(report.findings)}",
        "",
        "## Entries",
        "",
    ]
    if not report.entries:
        lines.append("- No snippet entries.")
    else:
        for entry in report.entries:
            span = f", lines {entry.line_span}" if entry.line_span else ""
            lines.append(
                f"- `{entry.snippet_id}` -> `{entry.source_path}`{span}; "
                f"{entry.extracted_line_count} line(s); preview: `{entry.preview}`"
            )

    lines.extend(["", "## Findings", ""])
    if not report.findings:
        lines.append("- No snippet-audit findings.")
        return "\n".join(lines)

    for finding in report.findings:
        lines.append(f"- [{finding.severity.upper()}] `{finding.code}`: {finding.message}")
    return "\n".join(lines)
