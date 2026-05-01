"""Shared utilities for validation submodules."""

from __future__ import annotations

from typing import Optional

from ..ooxml_inspector import normalize_font_name


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
