"""Deterministic visual checks on rendered page PNGs.

These checks use Pillow to analyze page images without AI.
They cover the audit classes defined in VISUAL_AUDIT_REQUIREMENTS.md:
- page geometry (aspect ratio)
- blank page detection (abnormal pagination)
- large white gap detection (figure/table break risk)
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image
import numpy as np

from .models import VisualAuditFinding

# A4 aspect ratio: height / width = 297/210 ≈ 1.4143
A4_ASPECT_RATIO = 297.0 / 210.0
# US Letter: 11/8.5 ≈ 1.2941
US_LETTER_ASPECT_RATIO = 11.0 / 8.5


def check_page_not_blank(png_path: Path, *, white_threshold: int = 250, max_white_ratio: float = 0.995) -> VisualAuditFinding | None:
    """Detect blank or near-blank pages.

    A page is considered blank if more than max_white_ratio of its pixels
    are near-white (all channels >= white_threshold).
    """
    with Image.open(png_path) as img:
        arr = np.array(img.convert("RGB"))
        white_pixels = np.all(arr >= white_threshold, axis=2)
        white_ratio = white_pixels.sum() / white_pixels.size

    if white_ratio > max_white_ratio:
        page_num = _page_number_from_path(png_path)
        return VisualAuditFinding(
            severity="warning",
            code="blank-page-detected",
            page=page_num,
            message=f"Page {page_num} appears blank ({white_ratio:.1%} white pixels).",
        )
    return None


def check_page_dimensions(
    png_path: Path,
    *,
    expected_ratio: float | None = None,
    tolerance: float = 0.05,
) -> VisualAuditFinding | None:
    """Verify page aspect ratio matches expected paper size.

    If expected_ratio is None, defaults to A4 (1.4143).
    """
    if expected_ratio is None:
        expected_ratio = A4_ASPECT_RATIO

    with Image.open(png_path) as img:
        width, height = img.size

    if width == 0:
        page_num = _page_number_from_path(png_path)
        return VisualAuditFinding(
            severity="error",
            code="invalid-page-image",
            page=page_num,
            message=f"Page {page_num} has zero width.",
        )

    actual_ratio = height / width
    if abs(actual_ratio - expected_ratio) > tolerance:
        page_num = _page_number_from_path(png_path)
        return VisualAuditFinding(
            severity="warning",
            code="page-aspect-ratio-mismatch",
            page=page_num,
            message=(
                f"Page {page_num} aspect ratio {actual_ratio:.4f} "
                f"differs from expected {expected_ratio:.4f} "
                f"(tolerance {tolerance})."
            ),
        )
    return None


def check_no_large_white_gaps(
    png_path: Path,
    *,
    white_threshold: int = 250,
    max_gap_ratio: float = 0.35,
    scan_band_height: int = 50,
) -> VisualAuditFinding | None:
    """Detect large contiguous white vertical bands.

    Scans horizontal bands of scan_band_height pixels. If a contiguous
    run of all-white bands exceeds max_gap_ratio of the page height,
    it indicates a potential layout gap (e.g., figure pushed to next page).
    """
    with Image.open(png_path) as img:
        arr = np.array(img.convert("RGB"))

    page_height = arr.shape[0]
    if page_height == 0:
        return None

    # Scan in horizontal bands
    max_contiguous = 0
    current_contiguous = 0

    for y_start in range(0, page_height, scan_band_height):
        y_end = min(y_start + scan_band_height, page_height)
        band = arr[y_start:y_end]
        white_pixels = np.all(band >= white_threshold, axis=2)
        band_white_ratio = white_pixels.sum() / white_pixels.size

        if band_white_ratio > 0.98:
            current_contiguous += (y_end - y_start)
        else:
            max_contiguous = max(max_contiguous, current_contiguous)
            current_contiguous = 0

    max_contiguous = max(max_contiguous, current_contiguous)
    gap_ratio = max_contiguous / page_height

    if gap_ratio > max_gap_ratio:
        page_num = _page_number_from_path(png_path)
        return VisualAuditFinding(
            severity="warning",
            code="large-white-gap",
            page=page_num,
            message=(
                f"Page {page_num} has a large white gap "
                f"({gap_ratio:.0%} of page height, threshold {max_gap_ratio:.0%})."
            ),
        )
    return None


def run_visual_checks(
    png_paths: list[Path],
    *,
    expected_aspect_ratio: float | None = None,
) -> list[VisualAuditFinding]:
    """Run all deterministic visual checks on a list of page PNGs."""
    findings: list[VisualAuditFinding] = []
    for png_path in png_paths:
        finding = check_page_not_blank(png_path)
        if finding:
            findings.append(finding)

        finding = check_page_dimensions(png_path, expected_ratio=expected_aspect_ratio)
        if finding:
            findings.append(finding)

        finding = check_no_large_white_gaps(png_path)
        if finding:
            findings.append(finding)

    return findings


def _page_number_from_path(png_path: Path) -> int:
    """Extract page number from filename like 'page-1.png'."""
    stem = png_path.stem
    if stem.startswith("page-"):
        try:
            return int(stem.split("-")[1])
        except (IndexError, ValueError):
            pass
    return 0
