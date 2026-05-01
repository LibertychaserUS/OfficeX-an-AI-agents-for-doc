"""End-to-end golden-path test for the full generation chain.

This test runs the complete pipeline from managed manifests through to
a finished docx, then opens the output and asserts the actual document
content matches expectations.  It covers:

    manifest_loader -> section_assembler -> writer -> validation -> candidate_audit

Unlike module-level tests that verify individual stages, this test
proves that the assembled pipeline produces a correct final artifact.
"""

from docx import Document
from pathlib import Path

from tools.report_scaffold_v3.section_pipeline import run_section_pipeline


def test_golden_path_pipeline_produces_correct_docx(tmp_path: Path):
    """Run the full section pipeline and verify the output document."""
    report = run_section_pipeline(pipeline_dir=tmp_path)

    # ---- pipeline report assertions ----
    assert report.output_docx.exists(), "Output docx was not created"
    assert report.build_source_path.exists(), "Build source was not written"
    assert report.candidate_audit_path.exists(), "Candidate audit was not written"
    assert report.validation_report_path.exists(), "Validation report was not written"

    assert report.candidate_error_count == 0, (
        f"Candidate audit has {report.candidate_error_count} error(s)"
    )
    assert report.validation_error_count == 0, (
        f"Validation has {report.validation_error_count} error(s)"
    )
    assert report.validation_warning_count == 0, (
        f"Validation has {report.validation_warning_count} warning(s)"
    )

    # ---- open the actual docx and verify content ----
    document = Document(str(report.output_docx))
    paragraphs = [p for p in document.paragraphs if p.text.strip()]

    # verify non-empty output
    assert len(paragraphs) >= 4, (
        f"Expected at least 4 non-empty paragraphs, got {len(paragraphs)}"
    )

    # verify heading structure
    heading_paragraphs = [
        p for p in paragraphs if p.style.name.startswith("Heading")
    ]
    assert len(heading_paragraphs) >= 2, (
        f"Expected at least 2 headings, got {len(heading_paragraphs)}"
    )

    # verify the first heading is the document title
    assert paragraphs[0].style.name == "Heading 1"
    assert "Document Operations System" in paragraphs[0].text

    # verify body paragraphs exist with Normal style
    normal_paragraphs = [p for p in paragraphs if p.style.name == "Normal"]
    assert len(normal_paragraphs) >= 1, "No Normal-style body paragraphs found"

    # verify appendix heading exists
    appendix_headings = [
        p for p in heading_paragraphs if "appendix" in p.text.lower()
    ]
    assert appendix_headings, "No appendix heading found in output"

    # verify page geometry (A4)
    section = document.sections[0]
    assert abs(section.page_width.pt - 595.3) < 1.0, (
        f"Page width {section.page_width.pt}pt is not A4"
    )
    assert abs(section.page_height.pt - 841.9) < 1.0, (
        f"Page height {section.page_height.pt}pt is not A4"
    )

    # verify style application on body paragraphs
    for p in normal_paragraphs:
        runs = p.runs
        assert len(runs) >= 1, f"Paragraph '{p.text[:40]}' has no runs"


def test_golden_path_pipeline_artifacts_are_consistent(tmp_path: Path):
    """Verify that pipeline artifacts are internally consistent."""
    import json

    report = run_section_pipeline(pipeline_dir=tmp_path)

    # candidate audit JSON should exist and parse
    candidate_audit_json = tmp_path / "candidate_audit.json"
    assert candidate_audit_json.exists()
    audit_data = json.loads(candidate_audit_json.read_text(encoding="utf-8"))
    assert audit_data["actual_paragraph_count"] == audit_data["expected_paragraph_count"], (
        f"Paragraph count mismatch: actual={audit_data['actual_paragraph_count']} "
        f"expected={audit_data['expected_paragraph_count']}"
    )
    assert audit_data["actual_heading_count"] == audit_data["expected_heading_count"], (
        f"Heading count mismatch: actual={audit_data['actual_heading_count']} "
        f"expected={audit_data['expected_heading_count']}"
    )

    # validation JSON should exist and parse
    validation_json = tmp_path / "validation.json"
    assert validation_json.exists()
    validation_data = json.loads(validation_json.read_text(encoding="utf-8"))
    error_findings = [
        f for f in validation_data["findings"] if f["severity"] == "error"
    ]
    assert not error_findings, (
        f"Validation errors found: {[f['message'] for f in error_findings]}"
    )
