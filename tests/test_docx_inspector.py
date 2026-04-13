from tools.report_scaffold_v3.docx_inspector import normalize_text, parse_figure_caption, slugify


def test_normalize_text_collapses_whitespace():
    assert normalize_text("  A   B\nC  ") == "A B C"


def test_slugify_is_stable():
    assert slugify("2.8.2 User Manual") == "2-8-2-user-manual"


def test_parse_figure_caption_extracts_id():
    parsed = parse_figure_caption("Figure 12.3: Guest login page")
    assert parsed is not None
    assert parsed["figure_id"] == "12.3"
    assert parsed["caption_tail"] == "Guest login page"


def test_parse_appendix_figure_caption_extracts_id():
    parsed = parse_figure_caption(
        "Appendix Figure A2: Full ER Diagram - LoopMart Database Schema"
    )
    assert parsed is not None
    assert parsed["label"] == "Appendix Figure"
    assert parsed["figure_id"] == "A2"
