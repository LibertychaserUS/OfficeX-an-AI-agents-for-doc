from __future__ import annotations

import json
from pathlib import Path

from tools.report_scaffold_v3.trace_indexer import (
    build_trace_index_report,
    parse_checkpoint_entry,
    write_trace_index,
)


def _write_checkpoint(trace_dir: Path, number: int, *, title: str, date: str, body: str) -> Path:
    trace_dir.mkdir(parents=True, exist_ok=True)
    path = trace_dir / f"CHECKPOINT_{number:02d}.md"
    path.write_text(f"# {title}\n\ndate: {date}\n\n{body}\n", encoding="utf-8")
    return path


def test_parse_checkpoint_entry_extracts_metadata_and_backfill(tmp_path: Path):
    checkpoint_path = _write_checkpoint(
        tmp_path,
        7,
        title="Checkpoint 07 - Trace Index",
        date="2026-03-31",
        body="This checkpoint documents a backfill recovery.",
    )

    entry = parse_checkpoint_entry(checkpoint_path)

    assert entry.checkpoint_number == 7
    assert entry.checkpoint_id == "CHECKPOINT_07"
    assert entry.path == checkpoint_path
    assert entry.title == "Checkpoint 07 - Trace Index"
    assert entry.date == "2026-03-31"
    assert entry.backfilled is True


def test_build_trace_index_report_orders_entries_and_tracks_missing_numbers(tmp_path: Path):
    trace_dir = tmp_path / "trace"
    first = _write_checkpoint(
        trace_dir,
        1,
        title="Checkpoint 01 - Start",
        date="2026-03-29",
        body="Initial checkpoint.",
    )
    _write_checkpoint(
        trace_dir,
        2,
        title="Checkpoint 02 - Mid",
        date="2026-03-30",
        body="Middle checkpoint.",
    )
    _write_checkpoint(
        trace_dir,
        4,
        title="Checkpoint 04 - Recovery",
        date="2026-03-31",
        body="Backfill recovery checkpoint.",
    )
    (trace_dir / "README.md").write_text("ignore me", encoding="utf-8")

    report = build_trace_index_report(trace_dir)

    assert report.trace_dir == trace_dir.resolve()
    assert report.checkpoint_count == 3
    assert report.latest_checkpoint_id == "CHECKPOINT_04"
    assert report.missing_numbers == [3]
    assert [entry.path for entry in report.entries] == [first, trace_dir / "CHECKPOINT_02.md", trace_dir / "CHECKPOINT_04.md"]
    assert [entry.checkpoint_id for entry in report.entries] == [
        "CHECKPOINT_01",
        "CHECKPOINT_02",
        "CHECKPOINT_04",
    ]
    assert report.entries[-1].backfilled is True


def test_write_trace_index_writes_json_and_markdown(tmp_path: Path):
    trace_dir = tmp_path / "trace"
    _write_checkpoint(
        trace_dir,
        1,
        title="Checkpoint 01 - Start",
        date="2026-03-29",
        body="Initial checkpoint.",
    )
    _write_checkpoint(
        trace_dir,
        2,
        title="Checkpoint 02 - Mid",
        date="2026-03-30",
        body="Middle checkpoint.",
    )

    report = build_trace_index_report(trace_dir)
    json_path, markdown_path = write_trace_index(report, trace_dir=trace_dir)

    assert json_path.exists()
    assert markdown_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["checkpoint_count"] == 2
    assert payload["latest_checkpoint_id"] == "CHECKPOINT_02"
    assert payload["missing_numbers"] == []
    assert len(payload["entries"]) == 2
    assert "Checkpoint Catalog" in markdown_path.read_text(encoding="utf-8")
    assert "CHECKPOINT_02" in markdown_path.read_text(encoding="utf-8")

