from pathlib import Path

from tools.report_scaffold_v3.models import LayoutContractManifest, TemplateProfileManifest
from tools.report_scaffold_v3.validation import build_validation_report


def make_inventory(figures, *, headings=None):
    return {
        "summary": {
            "paragraph_count": 10,
            "heading_count": 2,
            "figure_count": len(figures),
            "image_relationship_count": 2,
            "image_paragraph_count": len(figures),
            "section_count": 1,
            "appendix_heading_count": 1,
            "appendix_file_reference_count": 0,
        },
        "sections": [
            {
                "index": 0,
                "page_width_pt": 612.0,
                "page_height_pt": 792.0,
                "top_margin_pt": 72.0,
                "bottom_margin_pt": 72.0,
                "left_margin_pt": 90.0,
                "right_margin_pt": 90.0,
                "header_distance_pt": 36.0,
                "footer_distance_pt": 36.0,
            }
        ],
        "headings": headings or [],
        "figures": figures,
        "image_relationships": {
            "rId1": {"filename": "a.png", "reltype": "image", "target_ref": "media/a.png"},
            "rId2": {"filename": "b.png", "reltype": "image", "target_ref": "media/b.png"},
        },
    }


def make_template_profile():
    return TemplateProfileManifest(
        schema_version=1,
        template_id="template",
        source_template_docx=Path("/tmp/template.docx"),
        page_setup={
            "page_width_pt": 595.3,
            "page_height_pt": 841.9,
            "top_margin_pt": 70.9,
            "bottom_margin_pt": 70.9,
            "left_margin_pt": 70.9,
            "right_margin_pt": 70.9,
            "header_distance_pt": 42.55,
            "footer_distance_pt": 42.55,
        },
        style_contract={
            "Normal": {
                "effective_font": {"ascii": "Times New Roman", "east_asia": "宋体"},
                "effective_size_pt": 10.5,
                "alignment": "justify",
                "bold": False,
                "first_line_indent_pt": 0,
                "space_after_pt": 0,
                "line_spacing_multiple": 1.0,
            }
        },
    )


def make_layout_contract():
    return LayoutContractManifest(
        schema_version=1,
        template_id="template",
        image_layout_rules={
            "usable_body_width_pt": 453.5,
            "usable_body_height_pt": 700.1,
            "reserve_caption_space_pt": 48.0,
            "reserve_bottom_buffer_pt": 24.0,
        },
    )


def test_expected_wireframe_and_screenshot_pair_is_not_warning():
    inventory = make_inventory(
        [
            {
                "figure_label": "Figure",
                "figure_id": "8",
                "caption_tail": "Wireframe - Homepage",
                "caption_text": "Figure 8: Wireframe - Homepage",
                "caption_paragraph_index": 10,
                "image_paragraph_index": 9,
                "image_relationship_ids": ["rId1"],
                "image_extents_pt": [{"width_pt": 320.0, "height_pt": 180.0}],
            },
            {
                "figure_label": "Figure",
                "figure_id": "8",
                "caption_tail": "Screenshot - HomePage.jsx",
                "caption_text": "Figure 8: Screenshot - HomePage.jsx",
                "caption_paragraph_index": 20,
                "image_paragraph_index": 19,
                "image_relationship_ids": ["rId2"],
                "image_extents_pt": [{"width_pt": 320.0, "height_pt": 180.0}],
            },
        ]
    )

    report = build_validation_report(Path("/tmp/report.docx"), inventory)
    assert not [finding for finding in report.findings if finding.code == "duplicate-figure-id"]
    assert [finding for finding in report.findings if finding.code == "paired-evidence-figure-id-reuse"]


def test_non_paired_duplicate_stays_warning():
    inventory = make_inventory(
        [
            {
                "figure_label": "Figure",
                "figure_id": "8",
                "caption_tail": "Wireframe - Homepage",
                "caption_text": "Figure 8: Wireframe - Homepage",
                "caption_paragraph_index": 10,
                "image_paragraph_index": 9,
                "image_relationship_ids": ["rId1"],
                "image_extents_pt": [{"width_pt": 320.0, "height_pt": 180.0}],
            },
            {
                "figure_label": "Figure",
                "figure_id": "8",
                "caption_tail": "Wireframe - Search",
                "caption_text": "Figure 8: Wireframe - Search",
                "caption_paragraph_index": 20,
                "image_paragraph_index": 19,
                "image_relationship_ids": ["rId2"],
                "image_extents_pt": [{"width_pt": 320.0, "height_pt": 180.0}],
            },
        ]
    )

    report = build_validation_report(Path("/tmp/report.docx"), inventory)
    assert [finding for finding in report.findings if finding.code == "duplicate-figure-id"]


def test_reference_sample_template_drift_is_info_not_warning():
    inventory = make_inventory([])
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="reference_sample",
        format_authority_docx=Path("/tmp/template.docx"),
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        style_inventory={
            "styles": {
                "Normal": {
                    "ascii_font": "Times New Roman",
                    "east_asia_font": "宋体",
                    "size_pt": 10.5,
                    "alignment": "both",
                    "bold": False,
                    "first_line_indent_pt": 0,
                    "space_after_pt": 0,
                    "line_spacing_multiple": 1.0,
                }
            }
        },
    )
    page_drift = [
        finding for finding in report.findings if finding.code == "page-setup-differs-from-template"
    ]
    assert page_drift
    assert page_drift[0].severity == "info"


def test_reference_sample_body_run_override_drift_is_info():
    inventory = make_inventory([])
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="reference_sample",
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        override_inventory={
            "paragraphs": [
                {
                    "index": 4,
                    "style_name": "Normal",
                    "text_preview": "Body paragraph",
                    "fingerprint": "abc",
                    "direct_paragraph_formatting": {},
                    "run_override_count": 1,
                    "run_overrides": [
                        {
                            "run_index": 0,
                            "text_preview": "Body paragraph",
                            "direct_formatting": {"size_pt": 12.0},
                        }
                    ],
                }
            ]
        },
    )

    findings = [finding for finding in report.findings if finding.code == "run-direct-formatting-drift"]
    assert findings
    assert findings[0].severity == "info"


def test_candidate_output_body_run_override_drift_is_warning():
    inventory = make_inventory([])
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="candidate_output",
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        override_inventory={
            "paragraphs": [
                {
                    "index": 4,
                    "style_name": "Normal",
                    "text_preview": "Body paragraph",
                    "fingerprint": "abc",
                    "direct_paragraph_formatting": {},
                    "run_override_count": 1,
                    "run_overrides": [
                        {
                            "run_index": 0,
                            "text_preview": "Body paragraph",
                            "direct_formatting": {"size_pt": 12.0},
                        }
                    ],
                }
            ]
        },
    )

    findings = [finding for finding in report.findings if finding.code == "run-direct-formatting-drift"]
    assert findings
    assert findings[0].severity == "warning"


def test_reference_section_indent_override_stays_info_for_candidate_output():
    inventory = make_inventory(
        [],
        headings=[
            {"index": 8, "level": 2, "text": "1.6 References"},
            {"index": 20, "level": 2, "text": "1.7 Project Plan"},
        ],
    )
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="candidate_output",
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        override_inventory={
            "paragraphs": [
                {
                    "index": 12,
                    "style_name": "Normal",
                    "text_preview": "Reference entry",
                    "fingerprint": "ref-1",
                    "direct_paragraph_formatting": {"first_line_indent_pt": -36.0},
                    "run_override_count": 0,
                    "run_overrides": [],
                }
            ]
        },
    )

    findings = [
        finding for finding in report.findings if finding.code == "paragraph-direct-formatting-drift"
    ]
    assert findings
    assert findings[0].severity == "info"


def test_code_snippet_run_size_override_is_suppressed():
    inventory = make_inventory([])
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="reference_sample",
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        override_inventory={
            "paragraphs": [
                {
                    "index": 4,
                    "style_name": "Normal",
                    "text_preview": "package com.loopmart.app.dashboard.service;",
                    "fingerprint": "code-1",
                    "direct_paragraph_formatting": {},
                    "run_override_count": 2,
                    "run_overrides": [
                        {
                            "run_index": 0,
                            "text_preview": "package",
                            "direct_formatting": {"size_pt": 7.5},
                        },
                        {
                            "run_index": 1,
                            "text_preview": "com.loopmart.app.dashboard.service",
                            "direct_formatting": {"size_pt": 7.5},
                        },
                    ],
                }
            ]
        },
    )

    findings = [finding for finding in report.findings if finding.code == "run-direct-formatting-drift"]
    assert not findings


def test_emoji_font_fallback_override_is_suppressed():
    inventory = make_inventory([])
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="reference_sample",
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        override_inventory={
            "paragraphs": [
                {
                    "index": 4,
                    "style_name": "Normal",
                    "text_preview": "Feature icon",
                    "fingerprint": "emoji-1",
                    "direct_paragraph_formatting": {},
                    "run_override_count": 1,
                    "run_overrides": [
                        {
                            "run_index": 1,
                            "text_preview": "♻️",
                            "direct_formatting": {"ascii_font": "Segoe UI Emoji"},
                        }
                    ],
                }
            ]
        },
    )

    findings = [finding for finding in report.findings if finding.code == "run-direct-formatting-drift"]
    assert not findings


def test_reference_sample_seven_point_five_run_override_is_suppressed():
    inventory = make_inventory([])
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="reference_sample",
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        override_inventory={
            "paragraphs": [
                {
                    "index": 4,
                    "style_name": "Normal",
                    "text_preview": "Snippet line",
                    "fingerprint": "sample-75",
                    "direct_paragraph_formatting": {},
                    "run_override_count": 1,
                    "run_overrides": [
                        {
                            "run_index": 0,
                            "text_preview": "Snippet line",
                            "direct_formatting": {"size_pt": 7.5},
                        }
                    ],
                }
            ]
        },
    )

    findings = [finding for finding in report.findings if finding.code == "run-direct-formatting-drift"]
    assert not findings


def test_appendix_display_block_alignment_is_not_labeled_as_appendix_code():
    inventory = make_inventory(
        [],
        headings=[
            {"index": 20, "level": 1, "text": "Appendix — Full-Resolution UML Diagrams"},
            {"index": 30, "level": 1, "text": "Appendix — Complete Backend Source Code"},
        ],
    )
    report = build_validation_report(
        Path("/tmp/report.docx"),
        inventory,
        target_role="reference_sample",
        template_profile=make_template_profile(),
        layout_contract=make_layout_contract(),
        override_inventory={
            "paragraphs": [
                {
                    "index": 24,
                    "style_name": "Normal",
                    "text_preview": "",
                    "has_image": True,
                    "fingerprint": "appendix-display",
                    "direct_paragraph_formatting": {"alignment": "center"},
                    "run_override_count": 0,
                    "run_overrides": [],
                }
            ]
        },
    )

    findings = [
        finding for finding in report.findings if finding.code == "paragraph-direct-formatting-drift"
    ]
    assert findings
    assert "appendix figure or display block" in findings[0].message
    assert "appendix code" not in findings[0].message
