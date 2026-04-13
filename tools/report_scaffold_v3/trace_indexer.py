from __future__ import annotations

import json
import re
from pathlib import Path

from .models import CheckpointCatalogEntry, TraceIndexReport


CHECKPOINT_PATTERN = re.compile(r"CHECKPOINT_(\d+)\.md$")


def parse_checkpoint_entry(path: Path) -> CheckpointCatalogEntry:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    title = None
    date = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue
        if stripped.lower().startswith("date:"):
            date = stripped.split(":", 1)[1].strip()
            break

    match = CHECKPOINT_PATTERN.search(path.name)
    if match is None:
        raise ValueError(f"Not a checkpoint file: `{path}`.")
    checkpoint_number = int(match.group(1))
    backfilled = "backfill" in content.lower()
    return CheckpointCatalogEntry(
        checkpoint_number=checkpoint_number,
        checkpoint_id=f"CHECKPOINT_{checkpoint_number:02d}",
        path=path,
        title=title,
        date=date,
        backfilled=backfilled,
    )


def build_trace_index_report(trace_dir: Path) -> TraceIndexReport:
    trace_dir = trace_dir.expanduser().resolve()
    checkpoint_paths = sorted(
        [path for path in trace_dir.glob("CHECKPOINT_*.md") if CHECKPOINT_PATTERN.search(path.name)],
        key=lambda path: int(CHECKPOINT_PATTERN.search(path.name).group(1)),
    )
    entries = [parse_checkpoint_entry(path) for path in checkpoint_paths]
    numbers = [entry.checkpoint_number for entry in entries]
    missing_numbers: list[int] = []
    if numbers:
        expected = set(range(min(numbers), max(numbers) + 1))
        missing_numbers = sorted(expected - set(numbers))
    latest_checkpoint_id = entries[-1].checkpoint_id if entries else None
    return TraceIndexReport(
        trace_dir=trace_dir,
        checkpoint_count=len(entries),
        latest_checkpoint_id=latest_checkpoint_id,
        missing_numbers=missing_numbers,
        entries=entries,
    )


def render_trace_index_markdown(report: TraceIndexReport) -> str:
    lines = [
        "# Checkpoint Catalog",
        "",
        f"- Trace dir: `{report.trace_dir}`",
        f"- Checkpoint count: {report.checkpoint_count}",
        f"- Latest checkpoint: `{report.latest_checkpoint_id}`" if report.latest_checkpoint_id else "- Latest checkpoint: `[none]`",
        f"- Missing numbers: {', '.join(str(number) for number in report.missing_numbers)}"
        if report.missing_numbers
        else "- Missing numbers: none",
        "",
        "## Entries",
        "",
    ]
    if not report.entries:
        lines.append("- No checkpoint entries found.")
        return "\n".join(lines)

    for entry in report.entries:
        notes = []
        if entry.title:
            notes.append(entry.title)
        if entry.date:
            notes.append(entry.date)
        if entry.backfilled:
            notes.append("backfilled")
        note_text = " | ".join(notes) if notes else "no metadata"
        lines.append(f"- `{entry.checkpoint_id}` -> `{entry.path}` | {note_text}")
    return "\n".join(lines)


def write_trace_index(report: TraceIndexReport, *, trace_dir: Path) -> tuple[Path, Path]:
    trace_dir = trace_dir.expanduser().resolve()
    json_path = trace_dir / "checkpoint_catalog.json"
    markdown_path = trace_dir / "checkpoint_catalog.md"
    json_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text(render_trace_index_markdown(report).strip() + "\n", encoding="utf-8")
    return json_path, markdown_path
