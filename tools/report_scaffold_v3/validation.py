from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

from .docx_inspector import normalize_text
from .models import ValidationFinding, ValidationReport
from .ooxml_inspector import normalize_font_name

EXEMPT_OVERRIDE_ZONES = {
    "cover_page",
    "figure_caption_or_image_block",
    "appendix_figure_or_display_block",
    "bibliography_hanging_indent",
    "appendix_code",
    "code_snippet",
}


def classify_figure_evidence_kind(figure: dict) -> str:
    caption_tail = normalize_text(figure.get("caption_tail", "")).lower()
    if caption_tail.startswith("wireframe"):
        return "wireframe"
    if caption_tail.startswith("screenshot"):
        return "screenshot"
    return "other"


def summarize_ids(ids: list[str], *, limit: int = 12) -> str:
    ordered = sorted(ids, key=lambda value: (len(value), value))
    if len(ordered) <= limit:
        return ", ".join(ordered)
    head = ", ".join(ordered[:limit])
    return f"{head}, ... (+{len(ordered) - limit} more)"


def summarize_messages(messages: list[str], *, limit: int = 6) -> str:
    if len(messages) <= limit:
        return "; ".join(messages)
    head = "; ".join(messages[:limit])
    return f"{head}; ... (+{len(messages) - limit} more)"


def severity_for_role(
    target_role: str,
    *,
    strict_severity: str = "warning",
    sample_severity: str = "info",
) -> str:
    if target_role in {"template_authority", "candidate_output"}:
        return strict_severity
    return sample_severity


def as_mapping(value):
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def pt_matches(actual: Optional[float], expected: Optional[float], *, tolerance: float = 0.5) -> bool:
    if expected is None:
        return True
    if actual is None:
        return False
    return abs(actual - expected) <= tolerance


def normalize_alignment(value: Optional[str]) -> Optional[str]:
    if value == "both":
        return "justify"
    return value


def resolve_usable_dimensions(section: dict) -> tuple[Optional[float], Optional[float]]:
    usable_width = section.get("usable_body_width_pt")
    if usable_width is None:
        page_width = section.get("page_width_pt")
        left_margin = section.get("left_margin_pt")
        right_margin = section.get("right_margin_pt")
        if None not in {page_width, left_margin, right_margin}:
            usable_width = round(page_width - left_margin - right_margin, 2)

    usable_height = section.get("usable_body_height_pt")
    if usable_height is None:
        page_height = section.get("page_height_pt")
        top_margin = section.get("top_margin_pt")
        bottom_margin = section.get("bottom_margin_pt")
        if None not in {page_height, top_margin, bottom_margin}:
            usable_height = round(page_height - top_margin - bottom_margin, 2)

    return usable_width, usable_height


def build_page_setup_findings(
    inventory: dict,
    template_profile: Optional[dict],
    *,
    target_role: str,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    template_profile = as_mapping(template_profile)
    if not template_profile:
        return findings

    expected = template_profile.get("page_setup", {})
    severity = severity_for_role(target_role)
    for section in inventory.get("sections", []):
        mismatches = []
        for key in (
            "page_width_pt",
            "page_height_pt",
            "top_margin_pt",
            "bottom_margin_pt",
            "left_margin_pt",
            "right_margin_pt",
        ):
            if not pt_matches(section.get(key), expected.get(key)):
                mismatches.append(
                    f"{key} actual={section.get(key)} expected={expected.get(key)}"
                )
        if mismatches:
            findings.append(
                ValidationFinding(
                    severity=severity,
                    code="page-setup-differs-from-template",
                    message=(
                        f"Section {section.get('index', 0)} differs from the formatting template: "
                        + "; ".join(mismatches)
                    ),
                )
            )
    return findings


def style_has_expected_font(style: dict, expected_font: Optional[str]) -> bool:
    if expected_font is None:
        return True
    actual_fonts = {
        normalize_font_name(style.get("ascii_font")),
        normalize_font_name(style.get("hansi_font")),
        normalize_font_name(style.get("east_asia_font")),
    }
    return normalize_font_name(expected_font) in actual_fonts


def build_style_contract_findings(
    template_profile: Optional[dict],
    style_inventory: Optional[dict],
    *,
    target_role: str,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    template_profile = as_mapping(template_profile)
    style_inventory = as_mapping(style_inventory)
    if not template_profile or not style_inventory:
        return findings

    styles = style_inventory.get("styles") or style_inventory.get("styles_by_name") or {}
    normalized_styles = {name.lower(): style for name, style in styles.items()}
    severity = severity_for_role(target_role)
    for style_name, expected in template_profile.get("style_contract", {}).items():
        actual = styles.get(style_name) or normalized_styles.get(style_name.lower())
        if actual is None:
            findings.append(
                ValidationFinding(
                    severity=severity,
                    code="template-style-missing",
                    message=f"Style `{style_name}` is missing from the target docx.",
                )
            )
            continue

        mismatches = []
        expected_font = expected.get("effective_font", {}).get("ascii")
        if not style_has_expected_font(actual, expected_font):
            mismatches.append(
                f"font actual={actual.get('ascii_font')}/{actual.get('east_asia_font')} "
                f"expected~={expected.get('effective_font')}"
            )
        if not pt_matches(actual.get("size_pt"), expected.get("effective_size_pt"), tolerance=0.25):
            mismatches.append(
                f"size actual={actual.get('size_pt')} expected={expected.get('effective_size_pt')}"
            )
        if expected.get("bold") is not None and actual.get("bold") != expected.get("bold"):
            mismatches.append(f"bold actual={actual.get('bold')} expected={expected.get('bold')}")
        expected_alignment = normalize_alignment(expected.get("alignment"))
        actual_alignment = normalize_alignment(actual.get("alignment"))
        if expected_alignment not in {None, "inherit"} and actual_alignment != expected_alignment:
            mismatches.append(
                f"alignment actual={actual_alignment} expected={expected_alignment}"
            )
        if not pt_matches(
            actual.get("first_line_indent_pt"),
            expected.get("first_line_indent_pt"),
            tolerance=0.5,
        ):
            mismatches.append(
                "first_line_indent "
                f"actual={actual.get('first_line_indent_pt')} expected={expected.get('first_line_indent_pt')}"
            )
        if expected.get("line_spacing_multiple") is not None and not pt_matches(
            actual.get("line_spacing_multiple"),
            expected.get("line_spacing_multiple"),
            tolerance=0.05,
        ):
            mismatches.append(
                "line_spacing_multiple "
                f"actual={actual.get('line_spacing_multiple')} expected={expected.get('line_spacing_multiple')}"
            )
        if not pt_matches(actual.get("space_after_pt"), expected.get("space_after_pt"), tolerance=0.5):
            mismatches.append(
                f"space_after actual={actual.get('space_after_pt')} expected={expected.get('space_after_pt')}"
            )

        if mismatches:
            findings.append(
                ValidationFinding(
                    severity=severity,
                    code="style-differs-from-template",
                    message=f"Style `{style_name}` differs from the template: " + "; ".join(mismatches),
                )
            )
    return findings


def build_image_fit_findings(
    inventory: dict,
    layout_contract: Optional[dict],
    *,
    target_role: str,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    layout_contract = as_mapping(layout_contract)
    if not layout_contract:
        return findings

    sections = inventory.get("sections", [])
    if not sections:
        return findings

    usable_widths = []
    usable_heights = []
    for section in sections:
        usable_width, usable_height = resolve_usable_dimensions(section)
        if usable_width is not None:
            usable_widths.append(usable_width)
        if usable_height is not None:
            usable_heights.append(usable_height)

    if not usable_widths or not usable_heights:
        return findings

    rules = layout_contract.get("image_layout_rules", {})
    reserve_caption_space_pt = float(rules.get("reserve_caption_space_pt", 0) or 0)
    reserve_bottom_buffer_pt = float(rules.get("reserve_bottom_buffer_pt", 0) or 0)
    safe_width_pt = min(usable_widths)
    safe_height_pt = min(usable_heights) - reserve_caption_space_pt - reserve_bottom_buffer_pt
    severity = severity_for_role(target_role)

    overflow_messages: list[str] = []
    for figure in inventory.get("figures", []):
        for extent in figure.get("image_extents_pt", []):
            if extent["width_pt"] > safe_width_pt + 0.5:
                overflow_messages.append(
                    f"Figure `{figure['figure_id']}` width {extent['width_pt']}pt exceeds usable body width {safe_width_pt}pt"
                )
            if extent["height_pt"] > safe_height_pt + 0.5:
                overflow_messages.append(
                    f"Figure `{figure['figure_id']}` height {extent['height_pt']}pt exceeds safe body height {safe_height_pt}pt"
                )
    unique_messages = list(dict.fromkeys(overflow_messages))
    if unique_messages:
        findings.append(
            ValidationFinding(
                severity=severity,
                code="image-fit-risk",
                message=(
                    f"{len(unique_messages)} image fit risk item(s) detected: "
                    f"{summarize_messages(unique_messages)}."
                ),
            )
        )
    return findings


def normalize_override_zone(zone: str) -> str:
    return zone.replace("_", " ")


def comparable_value(property_name: str, value):
    if property_name == "alignment":
        return normalize_alignment(value)
    if "font" in property_name:
        return normalize_font_name(value)
    return value


def property_matches(property_name: str, actual, expected) -> bool:
    actual_value = comparable_value(property_name, actual)
    expected_value = comparable_value(property_name, expected)

    if property_name in {"size_pt"}:
        return pt_matches(actual_value, expected_value, tolerance=0.25)
    if property_name in {"line_spacing_multiple"}:
        return pt_matches(actual_value, expected_value, tolerance=0.05)
    if isinstance(actual_value, (int, float)) or isinstance(expected_value, (int, float)):
        return pt_matches(actual_value, expected_value, tolerance=0.5)
    return actual_value == expected_value


def format_cluster_value(value) -> str:
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def build_override_zone_context(inventory: dict) -> dict:
    headings = sorted(inventory.get("headings", []), key=lambda item: item["index"])
    first_heading_index = headings[0]["index"] if headings else None
    appendix_heading_indexes = [
        heading["index"] for heading in headings if "appendix" in heading["text"].lower()
    ]
    appendix_start_index = min(appendix_heading_indexes) if appendix_heading_indexes else None

    references_range = None
    for offset, heading in enumerate(headings):
        if "references" not in heading["text"].lower():
            continue
        start = heading["index"]
        end = headings[offset + 1]["index"] if offset + 1 < len(headings) else None
        references_range = (start, end)
        break

    figure_paragraph_indexes = set()
    for figure in inventory.get("figures", []):
        figure_paragraph_indexes.add(figure["caption_paragraph_index"])
        if figure.get("image_paragraph_index") is not None:
            figure_paragraph_indexes.add(figure["image_paragraph_index"])

    appendix_display_ranges = []
    for offset, heading in enumerate(headings):
        heading_text = heading["text"].lower()
        if "appendix" not in heading_text:
            continue
        if not any(token in heading_text for token in ("diagram", "uml", "er")):
            continue
        start = heading["index"]
        end = headings[offset + 1]["index"] if offset + 1 < len(headings) else None
        appendix_display_ranges.append((start, end))

    return {
        "first_heading_index": first_heading_index,
        "appendix_start_index": appendix_start_index,
        "references_range": references_range,
        "figure_paragraph_indexes": figure_paragraph_indexes,
        "appendix_display_ranges": appendix_display_ranges,
        "headings": headings,
    }


def looks_like_code_snippet(paragraph: dict) -> bool:
    text = (paragraph.get("text_preview") or "").strip()
    if len(text) < 12:
        return False
    code_markers = (
        "package ",
        "import ",
        "public ",
        "private ",
        "protected ",
        "class ",
        "interface ",
        "const ",
        "function ",
        "=>",
        "{",
        "}",
        ";",
        "@",
        "return ",
        "extends ",
        "implements ",
    )
    return any(marker in text for marker in code_markers)


def looks_like_appendix_figure_caption(paragraph: dict) -> bool:
    text = (paragraph.get("text_preview") or "").strip().lower()
    return text.startswith("appendix figure ")


def is_within_heading_window(index: int, heading_index: int, *, before: int = 20, after: int = 20) -> bool:
    return heading_index - before <= index <= heading_index + after


def classify_override_zone(paragraph: dict, zone_context: dict) -> str:
    index = paragraph["index"]
    headings = zone_context.get("headings", [])
    first_heading_index = zone_context.get("first_heading_index")
    if first_heading_index is not None and index < first_heading_index:
        return "cover_page"

    if index in zone_context.get("figure_paragraph_indexes", set()):
        return "figure_caption_or_image_block"

    for start, end in zone_context.get("appendix_display_ranges", []):
        if index >= start and (end is None or index < end):
            return "appendix_figure_or_display_block"

    if paragraph.get("has_image") or looks_like_appendix_figure_caption(paragraph):
        for heading in headings:
            heading_text = heading["text"].lower()
            if "appendix" not in heading_text:
                continue
            if not any(token in heading_text for token in ("diagram", "uml", "er")):
                continue
            if is_within_heading_window(index, heading["index"]):
                return "appendix_figure_or_display_block"

    appendix_start_index = zone_context.get("appendix_start_index")
    if appendix_start_index is not None and index >= appendix_start_index:
        return "appendix_code"

    references_range = zone_context.get("references_range")
    if references_range is not None:
        start, end = references_range
        if index >= start and (end is None or index < end):
            return "bibliography_hanging_indent"

    if looks_like_code_snippet(paragraph):
        return "code_snippet"

    return "body"


def severity_for_override_zone(target_role: str, zone: str) -> str:
    if target_role == "reference_sample":
        return "info"
    if zone in EXEMPT_OVERRIDE_ZONES:
        return "info"
    return severity_for_role(target_role)


def build_cluster_examples(items: list[dict], *, include_run_index: bool = False) -> str:
    rendered = []
    for item in items[:3]:
        location = f"p{item['paragraph_index']}"
        if include_run_index:
            location += f"/r{item['run_index']}"
        snippet = item.get("text_preview") or ""
        if snippet:
            rendered.append(f"{location} `{snippet[:60]}`")
        else:
            rendered.append(location)
    return ", ".join(rendered)


def is_font_fallback_override(run: dict, property_name: str, actual_value) -> bool:
    if property_name not in {"ascii_font", "hansi_font"}:
        return False
    if comparable_value(property_name, actual_value) not in {"Segoe UI Emoji", "Segoe UI Symbol"}:
        return False
    text = (run.get("text_preview") or "").strip()
    if not text:
        return False
    return not any(character.isalnum() for character in text)


def should_suppress_run_override(
    paragraph: dict,
    run: dict,
    property_name: str,
    actual_value,
    *,
    zone: str,
    target_role: str,
) -> bool:
    if is_font_fallback_override(run, property_name, actual_value):
        return True

    if (
        property_name == "size_pt"
        and actual_value == 7.5
        and (zone == "appendix_code" or target_role == "reference_sample")
    ):
        return True

    return False


def build_direct_override_findings(
    inventory: dict,
    template_profile: Optional[dict],
    override_inventory: Optional[dict],
    *,
    target_role: str,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    template_profile = as_mapping(template_profile)
    override_inventory = as_mapping(override_inventory)
    if not template_profile or not override_inventory:
        return findings

    style_contract = template_profile.get("style_contract", {})
    zone_context = build_override_zone_context(inventory)

    paragraph_clusters: dict[tuple, list[dict]] = defaultdict(list)
    run_clusters: dict[tuple, list[dict]] = defaultdict(list)

    paragraph_properties = (
        "alignment",
        "left_indent_pt",
        "right_indent_pt",
        "first_line_indent_pt",
        "space_before_pt",
        "space_after_pt",
        "line_spacing_multiple",
    )

    for paragraph in override_inventory.get("paragraphs", []):
        style_name = paragraph.get("style_name") or ""
        expected_style = style_contract.get(style_name)
        if not expected_style:
            continue

        zone = classify_override_zone(paragraph, zone_context)
        severity = severity_for_override_zone(target_role, zone)
        if zone == "code_snippet":
            continue
        direct_paragraph_formatting = paragraph.get("direct_paragraph_formatting") or {}

        for property_name in paragraph_properties:
            if property_name not in direct_paragraph_formatting:
                continue
            expected_value = expected_style.get(property_name)
            if expected_value in {None, "inherit"}:
                continue

            actual_value = direct_paragraph_formatting[property_name]
            if property_matches(property_name, actual_value, expected_value):
                continue

            cluster_key = (
                severity,
                zone,
                style_name,
                property_name,
                format_cluster_value(comparable_value(property_name, actual_value)),
                format_cluster_value(comparable_value(property_name, expected_value)),
            )
            paragraph_clusters[cluster_key].append(
                {
                    "paragraph_index": paragraph["index"],
                    "text_preview": paragraph.get("text_preview", ""),
                    "fingerprint": paragraph.get("fingerprint"),
                }
            )

        expected_font = expected_style.get("effective_font", {})
        expected_ascii = expected_font.get("ascii")
        expected_east_asia = expected_font.get("east_asia")
        expected_size_pt = expected_style.get("effective_size_pt")

        for run in paragraph.get("run_overrides", []):
            direct_run_formatting = run.get("direct_formatting") or {}
            run_checks = {
                "ascii_font": expected_ascii,
                "hansi_font": expected_ascii,
                "east_asia_font": expected_east_asia,
                "size_pt": expected_size_pt,
            }
            for property_name, expected_value in run_checks.items():
                if property_name not in direct_run_formatting or expected_value is None:
                    continue
                actual_value = direct_run_formatting[property_name]
                if should_suppress_run_override(
                    paragraph,
                    run,
                    property_name,
                    actual_value,
                    zone=zone,
                    target_role=target_role,
                ):
                    continue
                if property_matches(property_name, actual_value, expected_value):
                    continue

                cluster_key = (
                    severity,
                    zone,
                    style_name,
                    property_name,
                    format_cluster_value(comparable_value(property_name, actual_value)),
                    format_cluster_value(comparable_value(property_name, expected_value)),
                )
                run_clusters[cluster_key].append(
                    {
                        "paragraph_index": paragraph["index"],
                        "run_index": run["run_index"],
                        "text_preview": run.get("text_preview") or paragraph.get("text_preview", ""),
                        "fingerprint": paragraph.get("fingerprint"),
                    }
                )

    for (severity, zone, style_name, property_name, actual_value, expected_value), items in sorted(
        paragraph_clusters.items(), key=lambda entry: (-len(entry[1]), entry[0][1], entry[0][2], entry[0][3])
    ):
        findings.append(
            ValidationFinding(
                severity=severity,
                code="paragraph-direct-formatting-drift",
                message=(
                    f"{len(items)} paragraph(s) in {normalize_override_zone(zone)} use direct "
                    f"`{property_name}` overrides on style `{style_name}` with actual={actual_value} "
                    f"expected={expected_value}. Examples: {build_cluster_examples(items)}."
                ),
            )
        )

    for (severity, zone, style_name, property_name, actual_value, expected_value), items in sorted(
        run_clusters.items(), key=lambda entry: (-len(entry[1]), entry[0][1], entry[0][2], entry[0][3])
    ):
        findings.append(
            ValidationFinding(
                severity=severity,
                code="run-direct-formatting-drift",
                message=(
                    f"{len(items)} run(s) in {normalize_override_zone(zone)} directly override "
                    f"`{property_name}` on style `{style_name}` with actual={actual_value} "
                    f"expected={expected_value}. Examples: {build_cluster_examples(items, include_run_index=True)}."
                ),
            )
        )

    return findings


def build_validation_report(
    docx_path: Path,
    inventory: dict,
    *,
    target_role: str = "reference_sample",
    format_authority_docx: Optional[Path] = None,
    template_profile: Optional[dict] = None,
    layout_contract: Optional[dict] = None,
    style_inventory: Optional[dict] = None,
    override_inventory: Optional[dict] = None,
    ooxml_context: Optional[dict] = None,
) -> ValidationReport:
    findings: list[ValidationFinding] = []
    summary = dict(inventory["summary"])
    summary["target_docx_role"] = target_role

    if target_role == "reference_sample":
        message = "This document is being treated as a reference sample, not the authoritative formatting baseline."
        if format_authority_docx is not None:
            message += f" Formatting authority: `{format_authority_docx}`."
        findings.append(
            ValidationFinding(
                severity="info",
                code="reference-sample-mode",
                message=message,
            )
        )

    if summary["heading_count"] == 0:
        findings.append(
            ValidationFinding(
                severity="error",
                code="missing-headings",
                message="No heading paragraphs were detected in the target docx.",
            )
        )

    grouped_figures: dict[tuple[str, str], list[dict]] = defaultdict(list)
    if style_inventory is None and ooxml_context is not None:
        style_inventory = ooxml_context
    for figure in inventory["figures"]:
        grouped_figures[(figure["figure_label"], figure["figure_id"])].append(figure)

    paired_evidence_ids: list[str] = []
    for (figure_label, figure_id), figures in grouped_figures.items():
        if len(figures) <= 1:
            continue

        evidence_kinds = Counter(classify_figure_evidence_kind(figure) for figure in figures)
        is_expected_pair = (
            figure_label in {"Figure", "Fig."}
            and len(figures) == 2
            and evidence_kinds["wireframe"] == 1
            and evidence_kinds["screenshot"] == 1
        )

        if is_expected_pair:
            paired_evidence_ids.append(figure_id)
            continue

        findings.append(
            ValidationFinding(
                severity=severity_for_role(target_role),
                code="duplicate-figure-id",
                message=f"{figure_label} id `{figure_id}` appears {len(figures)} times.",
            )
        )

    if paired_evidence_ids:
        findings.append(
            ValidationFinding(
                severity="info",
                code="paired-evidence-figure-id-reuse",
                message=(
                    f"{len(paired_evidence_ids)} figure ids are reused as matched wireframe/screenshot "
                    f"evidence pairs: {summarize_ids(paired_evidence_ids)}."
                ),
            )
        )

    missing_bindings = [
        figure for figure in inventory["figures"] if figure["image_paragraph_index"] is None
    ]
    for figure in missing_bindings:
        findings.append(
            ValidationFinding(
                severity=severity_for_role(target_role),
                code="caption-without-image-binding",
                message=(
                    f"Caption `{figure['caption_text']}` at paragraph "
                    f"{figure['caption_paragraph_index']} does not have a nearby image binding."
                ),
            )
        )

    for figure in inventory["figures"]:
        for relationship_id in figure["image_relationship_ids"]:
            if relationship_id not in inventory["image_relationships"]:
                findings.append(
                    ValidationFinding(
                        severity="error",
                        code="missing-image-relationship",
                        message=(
                            f"Figure `{figure['figure_id']}` references missing image relationship "
                            f"`{relationship_id}`."
                        ),
                    )
                )

    if summary["appendix_heading_count"] == 0:
        findings.append(
            ValidationFinding(
                severity=severity_for_role(target_role),
                code="appendix-not-detected",
                message="No appendix heading was detected in the current docx import.",
            )
        )

    findings.extend(
        build_page_setup_findings(
            inventory,
            template_profile,
            target_role=target_role,
        )
    )
    findings.extend(
        build_style_contract_findings(
            template_profile,
            style_inventory,
            target_role=target_role,
        )
    )
    findings.extend(
        build_image_fit_findings(
            inventory,
            layout_contract,
            target_role=target_role,
        )
    )
    findings.extend(
        build_direct_override_findings(
            inventory,
            template_profile,
            override_inventory,
            target_role=target_role,
        )
    )

    findings.append(
        ValidationFinding(
            severity="info",
            code="validation-scope",
            message=(
                "This validator currently checks structural bindings, sample-vs-authority context, "
                "template/style drift, page geometry, and image-fit risk. Semantic section-to-code "
                "alignment will be added in later scaffold stages."
            ),
        )
    )

    return ValidationReport(source_docx=docx_path, summary=summary, findings=findings)


def render_validation_markdown(report: ValidationReport) -> str:
    lines = [
        "# Validation Report",
        "",
        f"- Source docx: `{report.source_docx}`",
        f"- Target role: `{report.summary.get('target_docx_role', 'unspecified')}`",
        f"- Paragraphs: {report.summary['paragraph_count']}",
        f"- Headings: {report.summary['heading_count']}",
        f"- Figures: {report.summary['figure_count']}",
        f"- Image relationships: {report.summary['image_relationship_count']}",
        "",
        "## Findings",
        "",
    ]
    for finding in report.findings:
        lines.append(f"- [{finding.severity.upper()}] `{finding.code}`: {finding.message}")
    return "\n".join(lines)
