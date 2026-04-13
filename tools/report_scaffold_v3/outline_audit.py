from __future__ import annotations

from collections import Counter
from pathlib import Path

from docx import Document

from .models import OutlineAuditReport, OutlineHeadingRecord


def extract_heading_level(paragraph) -> int | None:
    style_name = (paragraph.style.name or "").strip()
    lowered = style_name.lower()

    if lowered.startswith("heading "):
        suffix = style_name.split()[-1]
        if suffix.isdigit():
            return int(suffix)

    if lowered == "title":
        return 0
    if lowered == "subtitle":
        return 0
    return None


def scan_docx_outline(docx_path: Path) -> OutlineAuditReport:
    document = Document(str(docx_path))
    headings: list[OutlineHeadingRecord] = []

    for paragraph_index, paragraph in enumerate(document.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue

        level = extract_heading_level(paragraph)
        if level is None:
            continue

        headings.append(
            OutlineHeadingRecord(
                paragraph_index=paragraph_index,
                level=level,
                style_name=paragraph.style.name or "",
                text=text,
            )
        )

    level_counts = Counter(str(heading.level) for heading in headings)
    normalized_texts = [heading.text.strip().lower() for heading in headings]
    duplicate_heading_texts = sorted(
        {
            heading.text
            for heading in headings
            if normalized_texts.count(heading.text.strip().lower()) > 1
        }
    )
    appendix_heading_count = sum(1 for heading in headings if "appendix" in heading.text.lower())

    return OutlineAuditReport(
        source_docx=docx_path,
        heading_count=len(headings),
        appendix_heading_count=appendix_heading_count,
        heading_level_counts=dict(sorted(level_counts.items())),
        duplicate_heading_texts=duplicate_heading_texts,
        headings=headings,
    )


def render_outline_audit_markdown(report: OutlineAuditReport) -> str:
    lines = [
        "# Outline Audit Report",
        "",
        f"- Source docx: `{report.source_docx}`",
        f"- Heading count: {report.heading_count}",
        f"- Appendix heading count: {report.appendix_heading_count}",
        f"- Heading levels: {report.heading_level_counts}",
        "",
        "## Duplicate Headings",
        "",
    ]

    if not report.duplicate_heading_texts:
        lines.append("- No duplicate heading texts detected.")
    else:
        for text in report.duplicate_heading_texts:
            lines.append(f"- `{text}`")

    lines.extend(["", "## Heading Inventory", ""])
    for heading in report.headings[:50]:
        lines.append(
            f"- P{heading.paragraph_index} | L{heading.level} | `{heading.style_name}` | {heading.text}"
        )
    return "\n".join(lines)
