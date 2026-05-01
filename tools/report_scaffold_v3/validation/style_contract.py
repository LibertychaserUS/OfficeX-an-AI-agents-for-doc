"""Style contract validation against template profile."""

from __future__ import annotations

from typing import Optional

from ..models import ValidationFinding
from ..ooxml_inspector import normalize_font_name
from .common import as_mapping, normalize_alignment, pt_matches, severity_for_role


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
