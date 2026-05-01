"""Direct formatting override detection and zone classification."""

from __future__ import annotations

from collections import defaultdict
from typing import Optional

from ..docx_inspector import normalize_text
from ..models import ValidationFinding
from .common import (
    as_mapping,
    comparable_value,
    format_cluster_value,
    normalize_alignment,
    property_matches,
    severity_for_role,
)


EXEMPT_OVERRIDE_ZONES = {
    "cover_page",
    "figure_caption_or_image_block",
    "appendix_figure_or_display_block",
    "bibliography_hanging_indent",
    "appendix_code",
    "code_snippet",
}


def normalize_override_zone(zone: str) -> str:
    return zone.replace("_", " ")


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
