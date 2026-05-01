"""Image fit validation against layout contract."""

from __future__ import annotations

from typing import Optional

from ..models import ValidationFinding
from .common import as_mapping, resolve_usable_dimensions, severity_for_role, summarize_messages


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
