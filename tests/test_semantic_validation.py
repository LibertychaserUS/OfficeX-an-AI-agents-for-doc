"""Tests for semantic validation engine."""

from tools.report_scaffold_v3.semantic_validation import (
    run_semantic_validation,
    check_citation_references,
    check_numbering_continuity,
    check_appendix_alignment,
    check_section_references,
    check_terminology_consistency,
)


def _p(index, text, style="Normal"):
    return {"index": index, "text": text, "style": style}


# ---- Citation checks ----

def test_citation_missing_from_bibliography():
    paras = [
        _p(0, "Introduction", "Heading 1"),
        _p(1, "As shown by (Smith, 2024), the results are clear."),
        _p(2, "Also see (Jones, 2023) for further details."),
        _p(3, "References", "Heading 1"),
        _p(4, "Smith, J. (2024) A Study of Things. Journal of Stuff."),
    ]
    findings = check_citation_references(paras)
    # Jones, 2023 is cited but not in bibliography
    jones_findings = [f for f in findings if "Jones" in f.message]
    assert jones_findings
    # Smith, 2024 should be found
    smith_findings = [f for f in findings if "Smith" in f.message]
    assert not smith_findings


def test_citation_all_present():
    paras = [
        _p(0, "Introduction", "Heading 1"),
        _p(1, "According to (Smith, 2024), this is true."),
        _p(2, "References", "Heading 1"),
        _p(3, "Smith, J. (2024) A Study. Journal."),
    ]
    findings = check_citation_references(paras)
    assert not findings


# ---- Numbering checks ----

def test_figure_numbering_gap():
    paras = [
        _p(0, "See Figure 1 for details."),
        _p(1, "Figure 3 shows the result."),  # gap: Figure 2 missing
    ]
    findings = check_numbering_continuity(paras)
    gap_findings = [f for f in findings if "gap" in f.code]
    assert gap_findings


def test_figure_numbering_continuous():
    paras = [
        _p(0, "See Figure 1 for details."),
        _p(1, "Figure 2 shows the result."),
        _p(2, "Figure 3 confirms it."),
    ]
    findings = check_numbering_continuity(paras)
    gap_findings = [f for f in findings if "gap" in f.code]
    assert not gap_findings


def test_table_numbering_duplicate():
    paras = [
        _p(0, "Table 1 shows data."),
        _p(1, "Table 1 has more data."),  # duplicate
        _p(2, "Table 2 summarizes."),
    ]
    findings = check_numbering_continuity(paras)
    dupe_findings = [f for f in findings if "duplicate" in f.code]
    assert dupe_findings


# ---- Appendix alignment ----

def test_appendix_referenced_but_missing():
    paras = [
        _p(0, "See Appendix A for the full source code."),
        _p(1, "See Appendix C for the wireframes."),
        _p(2, "Appendix A: Source Code", "Heading 1"),
        # Appendix C is referenced but doesn't exist as a heading
    ]
    findings = check_appendix_alignment(paras)
    assert any("Appendix C" in f.message for f in findings)


def test_appendix_all_aligned():
    paras = [
        _p(0, "See Appendix A for details."),
        _p(1, "Appendix A: Details", "Heading 1"),
    ]
    findings = check_appendix_alignment(paras)
    assert not findings


# ---- Section references ----

def test_section_reference_missing():
    paras = [
        _p(0, "1 Introduction", "Heading 1"),
        _p(1, "As discussed in Section 3.2, this is important."),
        _p(2, "2 Methodology", "Heading 1"),
    ]
    findings = check_section_references(paras)
    assert any("3.2" in f.message for f in findings)


# ---- Terminology consistency ----

def test_terminology_variants_detected():
    paras = [
        _p(0, "Machine Learning is important."),
        _p(1, "We use machine learning techniques."),
        _p(2, "The Machine Learning model works."),
        _p(3, "Apply machine learning to this problem."),
    ]
    findings = check_terminology_consistency(paras, min_occurrences=2)
    term_findings = [f for f in findings if f.code == "terminology-variant"]
    assert term_findings


# ---- Full pipeline ----

def test_full_semantic_validation():
    paras = [
        _p(0, "1 Introduction", "Heading 1"),
        _p(1, "This study (Smith, 2024) examines machine learning."),
        _p(2, "See Figure 1 and Table 1 for results."),
        _p(3, "Figure 1: Accuracy chart", "Normal"),
        _p(4, "Table 1: Metrics summary", "Normal"),
        _p(5, "See Appendix A for source code."),
        _p(6, "2 Results", "Heading 1"),
        _p(7, "As discussed in Section 1, the approach works."),
        _p(8, "References", "Heading 1"),
        _p(9, "Smith, J. (2024) Machine Learning Study. Journal."),
        _p(10, "Appendix A: Source Code", "Heading 1"),
        _p(11, "def main(): pass"),
    ]
    report = run_semantic_validation(paras, source_label="test_doc")

    assert report.source == "test_doc"
    assert len(report.checks_run) == 6
    assert report.error_count == 0
