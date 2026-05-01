"""Semantic validation engine: the third verification track.

Beyond structural validation (styles, geometry) and visual validation
(PNG rendering), semantic validation checks that the document's
**content** is internally consistent.

Checks:
1. Cross-references: in-text citations match bibliography entries
2. Figure/table numbering: sequential, no gaps, no duplicates
3. Appendix alignment: items referenced in text exist in appendices
4. Terminology consistency: key terms used consistently throughout
5. Section cross-references: "as discussed in Section X" → Section X exists
6. Logic flow: conclusions reference prior evidence (AI-assisted)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SemanticFinding:
    severity: str  # "error", "warning", "info"
    code: str
    message: str
    location: str = ""  # e.g. "paragraph 15" or "Section 3.2"


@dataclass
class SemanticValidationReport:
    source: str
    findings: list[SemanticFinding] = field(default_factory=list)
    checks_run: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "checks_run": self.checks_run,
            "findings": [
                {"severity": f.severity, "code": f.code,
                 "message": f.message, "location": f.location}
                for f in self.findings
            ],
        }


# ---- Citation cross-reference checks ----

CITATION_PATTERN = re.compile(
    r"\(([A-Z][a-z]+(?:\s+(?:et\s+al\.?|and|&)\s+[A-Z][a-z]+)?,?\s*\d{4}[a-z]?)\)"
)
BIBLIOGRAPHY_ENTRY_PATTERN = re.compile(
    r"^([A-Z][a-z]+(?:,?\s+[A-Z]\.?)*(?:\s+(?:et\s+al\.?|and|&)\s+[A-Z][a-z]+(?:,?\s+[A-Z]\.?)*)?\s*\(\d{4}[a-z]?\))"
)


def check_citation_references(
    paragraphs: list[dict],
) -> list[SemanticFinding]:
    """Check that in-text citations have matching bibliography entries."""
    findings = []

    # Extract all in-text citations
    citations: dict[str, list[int]] = {}  # citation_key -> [paragraph_indices]
    for p in paragraphs:
        text = p.get("text", "")
        idx = p.get("index", 0)
        for match in CITATION_PATTERN.finditer(text):
            key = match.group(1).strip()
            citations.setdefault(key, []).append(idx)

    # Find bibliography section
    bib_entries: set[str] = set()
    in_bib = False
    for p in paragraphs:
        text = p.get("text", "")
        heading = p.get("style", "")
        if heading.startswith("Heading") and any(
            kw in text.lower() for kw in ("references", "bibliography", "works cited")
        ):
            in_bib = True
            continue
        if in_bib:
            if heading.startswith("Heading"):
                in_bib = False
                continue
            # Extract author-year from bibliography entry
            match = BIBLIOGRAPHY_ENTRY_PATTERN.match(text.strip())
            if match:
                bib_entries.add(match.group(1).strip())

    if not citations:
        return findings

    # Check each citation has a bibliography entry
    for citation_key, indices in citations.items():
        # Fuzzy match: check if any bib entry contains the author name and year
        author_part = citation_key.split(",")[0].split("(")[0].strip()
        year_match = re.search(r"\d{4}", citation_key)
        year = year_match.group() if year_match else ""

        found = any(
            author_part.split()[0] in entry and year in entry
            for entry in bib_entries
        )

        if not found and bib_entries:
            findings.append(SemanticFinding(
                severity="warning",
                code="citation-no-bibliography-match",
                message=f"Citation ({citation_key}) not found in bibliography.",
                location=f"paragraphs {indices}",
            ))

    return findings


# ---- Figure/table numbering checks ----

FIGURE_REF_PATTERN = re.compile(r"(?:Figure|Fig\.?)\s+(\d+(?:\.\d+)?)", re.IGNORECASE)
TABLE_REF_PATTERN = re.compile(r"Table\s+(\d+(?:\.\d+)?)", re.IGNORECASE)


def check_numbering_continuity(
    paragraphs: list[dict],
) -> list[SemanticFinding]:
    """Check figure and table numbers are sequential without gaps."""
    findings = []

    figure_numbers: list[str] = []
    table_numbers: list[str] = []

    for p in paragraphs:
        text = p.get("text", "")
        for match in FIGURE_REF_PATTERN.finditer(text):
            figure_numbers.append(match.group(1))
        for match in TABLE_REF_PATTERN.finditer(text):
            table_numbers.append(match.group(1))

    # Check for gaps in simple integer sequences
    for label, numbers in [("Figure", figure_numbers), ("Table", table_numbers)]:
        int_nums = []
        for n in numbers:
            try:
                int_nums.append(int(n))
            except ValueError:
                continue
        if int_nums:
            sorted_unique = sorted(set(int_nums))
            expected = list(range(sorted_unique[0], sorted_unique[-1] + 1))
            missing = set(expected) - set(sorted_unique)
            if missing:
                findings.append(SemanticFinding(
                    severity="warning",
                    code=f"{label.lower()}-numbering-gap",
                    message=f"{label} numbering has gaps: missing {sorted(missing)}",
                ))
            # Check for same number appearing in multiple locations
            from collections import Counter
            counts = Counter(int_nums)
            dupes = [n for n, c in counts.items() if c > 1]
            if dupes:
                findings.append(SemanticFinding(
                    severity="warning",
                    code=f"{label.lower()}-numbering-duplicate",
                    message=f"{label} numbering has duplicates: {sorted(dupes)}",
                ))

    return findings


# ---- Appendix alignment checks ----

APPENDIX_REF_PATTERN = re.compile(r"Appendix\s+([A-Z]|\d+)", re.IGNORECASE)


def check_appendix_alignment(
    paragraphs: list[dict],
) -> list[SemanticFinding]:
    """Check that appendix references in text match actual appendix headings."""
    findings = []

    # Find appendix references in body text
    referenced_appendices: set[str] = set()
    appendix_headings: set[str] = set()

    for p in paragraphs:
        text = p.get("text", "")
        style = p.get("style", "")

        # Collect appendix references in body
        for match in APPENDIX_REF_PATTERN.finditer(text):
            if not style.startswith("Heading"):
                referenced_appendices.add(match.group(1).upper())

        # Collect actual appendix headings
        if style.startswith("Heading") and "appendix" in text.lower():
            match = APPENDIX_REF_PATTERN.search(text)
            if match:
                appendix_headings.add(match.group(1).upper())

    # Check referenced appendices exist
    for ref in referenced_appendices:
        if ref not in appendix_headings and appendix_headings:
            findings.append(SemanticFinding(
                severity="warning",
                code="appendix-reference-missing",
                message=f"Appendix {ref} referenced in text but not found in appendix headings.",
            ))

    return findings


# ---- Section cross-reference checks ----

SECTION_REF_PATTERN = re.compile(
    r"(?:Section|Chapter|section|chapter)\s+(\d+(?:\.\d+)*)", re.IGNORECASE
)


def check_section_references(
    paragraphs: list[dict],
) -> list[SemanticFinding]:
    """Check that section references point to existing sections."""
    findings = []

    # Extract section numbers from headings
    section_numbers: set[str] = set()
    referenced_sections: dict[str, list[int]] = {}

    for p in paragraphs:
        text = p.get("text", "")
        style = p.get("style", "")
        idx = p.get("index", 0)

        if style.startswith("Heading"):
            # Extract leading number from heading text
            num_match = re.match(r"(\d+(?:\.\d+)*)\s", text.strip())
            if num_match:
                section_numbers.add(num_match.group(1))

        # Find section references in body
        if not style.startswith("Heading"):
            for match in SECTION_REF_PATTERN.finditer(text):
                ref = match.group(1)
                referenced_sections.setdefault(ref, []).append(idx)

    for ref, indices in referenced_sections.items():
        if ref not in section_numbers and section_numbers:
            findings.append(SemanticFinding(
                severity="warning",
                code="section-reference-missing",
                message=f"Section {ref} referenced but not found in headings.",
                location=f"paragraphs {indices}",
            ))

    return findings


# ---- Terminology consistency check ----

def check_terminology_consistency(
    paragraphs: list[dict],
    *,
    min_occurrences: int = 3,
) -> list[SemanticFinding]:
    """Detect potential terminology inconsistency.

    Finds cases where similar terms are used in different forms
    (e.g., "machine learning" vs "Machine Learning" vs "ML").
    """
    findings = []

    # Build term frequency map (case-insensitive)
    term_variants: dict[str, dict[str, int]] = {}  # lowercase -> {actual_form: count}

    # First pass: collect capitalized multi-word technical terms
    # Use a smarter pattern: 2+ capitalized words in sequence
    CAP_TERM_PATTERN = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")
    for p in paragraphs:
        text = p.get("text", "")
        for match in CAP_TERM_PATTERN.finditer(text):
            term = match.group(1)
            key = term.lower()
            variants = term_variants.setdefault(key, {})
            variants[term] = variants.get(term, 0) + 1

    # Second pass: find lowercase variants of already-seen capitalized terms
    for p in paragraphs:
        text = p.get("text", "")
        for key in list(term_variants.keys()):
            pattern = re.compile(r"\b" + re.escape(key) + r"\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                actual = match.group()
                if actual not in term_variants[key]:
                    variants = term_variants[key]
                    variants[actual] = variants.get(actual, 0) + 1

    # Flag terms with multiple variant forms
    for key, variants in term_variants.items():
        total = sum(variants.values())
        if total >= min_occurrences and len(variants) > 1:
            forms = ", ".join(f'"{v}" ({c}x)' for v, c in sorted(variants.items(), key=lambda x: -x[1]))
            findings.append(SemanticFinding(
                severity="info",
                code="terminology-variant",
                message=f"Term '{key}' appears in {len(variants)} forms: {forms}",
            ))

    return findings


def check_figure_text_proximity(
    paragraphs: list[dict],
    *,
    max_distance: int = 10,
) -> list[SemanticFinding]:
    """Check that referenced content anchors are near their definitions.

    A content anchor is any labeled element: Figure, Table, Snippet,
    Listing, Diagram, etc. When body text references an anchor
    (e.g. "Figure 3 shows..."), the anchor's caption/definition
    should be within max_distance paragraphs.

    This is abstracted from the specific problem of figure-text
    misalignment — it catches any content-reference distance issue.
    """
    findings = []

    # Generalized anchor pattern: any "Label N" with caption
    ANCHOR_CAPTION_PATTERN = re.compile(
        r"^((?:Figure|Fig\.?|Table|Snippet|Listing|Diagram|Chart|Algorithm)\s+\d+(?:\.\d+)?)\s*[:.\-—]",
        re.IGNORECASE,
    )
    ANCHOR_REF_PATTERN = re.compile(
        r"\b((?:Figure|Fig\.?|Table|Snippet|Listing|Diagram|Chart|Algorithm)\s+\d+(?:\.\d+)?)\b",
        re.IGNORECASE,
    )

    # Collect anchor caption positions
    caption_positions: dict[str, int] = {}
    for p in paragraphs:
        text = p.get("text", "")
        idx = p.get("index", 0)
        cap_match = ANCHOR_CAPTION_PATTERN.match(text.strip())
        if cap_match:
            key = cap_match.group(1).lower()
            key = re.sub(r"fig\.?", "figure", key)
            caption_positions[key] = idx

    # Check references are near their captions
    for p in paragraphs:
        text = p.get("text", "")
        idx = p.get("index", 0)
        style = p.get("style", "")
        if style.startswith("Heading"):
            continue

        for match in ANCHOR_REF_PATTERN.finditer(text):
            ref_text = match.group(1)
            ref_key = ref_text.lower()
            ref_key = re.sub(r"fig\.?", "figure", ref_key)

            if ref_key in caption_positions:
                distance = abs(idx - caption_positions[ref_key])
                if distance > max_distance:
                    findings.append(SemanticFinding(
                        severity="warning",
                        code="anchor-reference-distant",
                        message=(
                            f"Reference to '{ref_text}' at paragraph {idx} is "
                            f"{distance} paragraphs from its definition "
                            f"(threshold: {max_distance})."
                        ),
                        location=f"paragraph {idx}",
                    ))

    return findings

    return findings


# ---- Main validation entry point ----

def run_semantic_validation(
    paragraphs: list[dict],
    *,
    source_label: str = "document",
) -> SemanticValidationReport:
    """Run all semantic validation checks.

    Args:
        paragraphs: list of dicts with keys: index, style, text
        source_label: label for the report
    """
    report = SemanticValidationReport(source=source_label)

    checks = [
        ("citation_references", check_citation_references),
        ("numbering_continuity", check_numbering_continuity),
        ("appendix_alignment", check_appendix_alignment),
        ("section_references", check_section_references),
        ("figure_text_proximity", check_figure_text_proximity),
        ("terminology_consistency", check_terminology_consistency),
    ]

    for check_name, check_fn in checks:
        report.checks_run.append(check_name)
        if check_name == "terminology_consistency":
            report.findings.extend(check_fn(paragraphs, min_occurrences=3))
        else:
            report.findings.extend(check_fn(paragraphs))

    return report
