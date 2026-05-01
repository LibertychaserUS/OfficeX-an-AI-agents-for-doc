"""Page setup validation against template profile."""

from __future__ import annotations

from typing import Optional

from ..models import ValidationFinding
from .common import as_mapping, pt_matches, severity_for_role


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
