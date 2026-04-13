from pathlib import Path

import yaml

from tools.report_scaffold_v3.snippet_audit import (
    build_snippet_audit,
    render_snippet_audit_markdown,
)


def test_build_snippet_audit_reports_entries_for_valid_manifest(tmp_path: Path):
    literal_source = tmp_path / "literal_source.txt"
    literal_source.write_text("alpha\nbeta\n", encoding="utf-8")
    line_source = tmp_path / "line_source.py"
    line_source.write_text("line 1\nline 2\nline 3\n", encoding="utf-8")

    manifest_path = tmp_path / "snippets.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "managed_snippets": [
                    {
                        "snippet_id": "SNIP-LIT-01",
                        "title": "Literal Demo",
                        "language": "text",
                        "source_path": str(literal_source),
                        "target_section_id": "section-a",
                        "placement": "after_section",
                        "order": 2,
                        "extract_mode": "literal_text",
                        "literal_text": "\nalpha\nbeta\n",
                    },
                    {
                        "snippet_id": "SNIP-LINE-01",
                        "title": "Line Demo",
                        "language": "python",
                        "source_path": str(line_source),
                        "target_section_id": "section-a",
                        "placement": "after_section",
                        "order": 1,
                        "extract_mode": "line_range",
                        "start_line": 2,
                        "end_line": 3,
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    report = build_snippet_audit(manifest_path)
    markdown = render_snippet_audit_markdown(report)

    assert report.snippets_checked == 2
    assert len(report.entries) == 2
    assert not report.findings
    assert [entry.snippet_id for entry in report.entries] == ["SNIP-LIT-01", "SNIP-LINE-01"]
    assert report.entries[0].preview == "alpha"
    assert report.entries[1].line_span == "2-3"
    assert "Snippet Audit Report" in markdown
    assert "No snippet-audit findings." in markdown


def test_build_snippet_audit_flags_bad_snippet_ranges(tmp_path: Path):
    valid_source = tmp_path / "valid_source.py"
    valid_source.write_text("line 1\nline 2\nline 3\n", encoding="utf-8")

    manifest_path = tmp_path / "snippets_bad.yml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "managed_snippets": [
                    {
                        "snippet_id": "SNIP-OK-01",
                        "title": "Valid Demo",
                        "language": "python",
                        "source_path": str(valid_source),
                        "target_section_id": "section-a",
                        "placement": "after_section",
                        "order": 1,
                        "extract_mode": "line_range",
                        "start_line": 1,
                        "end_line": 2,
                    },
                    {
                        "snippet_id": "SNIP-BAD-01",
                        "title": "Invalid Demo",
                        "language": "python",
                        "source_path": str(valid_source),
                        "target_section_id": "section-a",
                        "placement": "after_section",
                        "order": 2,
                        "extract_mode": "line_range",
                        "start_line": 3,
                        "end_line": 2,
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    report = build_snippet_audit(manifest_path)
    markdown = render_snippet_audit_markdown(report)

    assert report.snippets_checked == 2
    assert len(report.entries) == 1
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.severity == "error"
    assert finding.code == "snippet-extraction-failed"
    assert "invalid line range" in finding.message
    assert "[ERROR]" in markdown
    assert "snippet-extraction-failed" in markdown
