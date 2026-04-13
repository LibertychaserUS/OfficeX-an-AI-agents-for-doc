from __future__ import annotations

from datetime import date
from pathlib import Path

from .models import OfficeXTraceCheckpointReport
from .paths import TRACE_DIR
from .trace_indexer import build_trace_index_report, write_trace_index


def _next_checkpoint_number(trace_dir: Path) -> int:
    report = build_trace_index_report(trace_dir)
    if not report.entries:
        return 1
    return max(entry.checkpoint_number for entry in report.entries) + 1


def render_trace_checkpoint_markdown(
    *,
    checkpoint_id: str,
    title: str,
    summary_lines: list[str],
    verification_lines: list[str],
    follow_up_lines: list[str],
) -> str:
    lines = [
        f"# {checkpoint_id}",
        "",
        f"date: {date.today().isoformat()}",
        "",
        "## Title",
        "",
        title,
        "",
        "## Summary",
        "",
    ]
    if summary_lines:
        for line in summary_lines:
            lines.append(f"- {line}")
    else:
        lines.append("- No summary lines recorded.")

    lines.extend(["", "## Verification", ""])
    if verification_lines:
        for line in verification_lines:
            lines.append(f"- {line}")
    else:
        lines.append("- Verification not yet recorded.")

    lines.extend(["", "## Follow-up", ""])
    if follow_up_lines:
        for line in follow_up_lines:
            lines.append(f"- {line}")
    else:
        lines.append("- No follow-up items recorded.")
    return "\n".join(lines)


def render_trace_catalog_summary(report: dict) -> str:
    lines = [
        "# Trace Catalog Summary",
        "",
        f"- Trace dir: `{report['trace_dir']}`",
        f"- Checkpoint count: {report['checkpoint_count']}",
        f"- Latest checkpoint: `{report['latest_checkpoint_id']}`"
        if report["latest_checkpoint_id"]
        else "- Latest checkpoint: `[none]`",
    ]
    if report["missing_numbers"]:
        lines.append(
            f"- Missing checkpoint numbers: {', '.join(str(number) for number in report['missing_numbers'])}"
        )
    else:
        lines.append("- Missing checkpoint numbers: none")
    return "\n".join(lines)


def create_trace_checkpoint(
    *,
    title: str,
    summary_lines: list[str] | None = None,
    verification_lines: list[str] | None = None,
    follow_up_lines: list[str] | None = None,
    trace_dir: Path = TRACE_DIR,
) -> OfficeXTraceCheckpointReport:
    resolved_trace_dir = trace_dir.expanduser().resolve()
    resolved_trace_dir.mkdir(parents=True, exist_ok=True)
    summary_lines = summary_lines or []
    verification_lines = verification_lines or []
    follow_up_lines = follow_up_lines or []

    checkpoint_number = _next_checkpoint_number(resolved_trace_dir)
    checkpoint_id = f"CHECKPOINT_{checkpoint_number:02d}"
    checkpoint_path = resolved_trace_dir / f"{checkpoint_id}.md"
    checkpoint_path.write_text(
        render_trace_checkpoint_markdown(
            checkpoint_id=checkpoint_id,
            title=title,
            summary_lines=summary_lines,
            verification_lines=verification_lines,
            follow_up_lines=follow_up_lines,
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    report = build_trace_index_report(resolved_trace_dir)
    write_trace_index(report, trace_dir=resolved_trace_dir)
    (resolved_trace_dir / "checkpoint_catalog_summary.md").write_text(
        render_trace_catalog_summary(report.model_dump(mode="json")).strip() + "\n",
        encoding="utf-8",
    )
    return OfficeXTraceCheckpointReport(
        checkpoint_id=checkpoint_id,
        checkpoint_path=checkpoint_path,
        trace_dir=resolved_trace_dir,
        title=title,
        summary_lines=summary_lines,
        verification_lines=verification_lines,
        follow_up_lines=follow_up_lines,
    )
