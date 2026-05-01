"""OfficeX diff: visual comparison of two docx files.

Renders both documents to PNG via LibreOffice, then performs
per-page image comparison to highlight differences.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from .visual_audit import render_docx_to_png

logger = logging.getLogger(__name__)


@dataclass
class DiffPageResult:
    page: int
    similarity: float  # 0.0 = completely different, 1.0 = identical
    diff_png_path: Path | None = None
    changed: bool = False


@dataclass
class DiffReport:
    docx_a: Path
    docx_b: Path
    status: str  # "success", "render_failed", "page_count_mismatch"
    pages_a: int = 0
    pages_b: int = 0
    page_results: list[DiffPageResult] = field(default_factory=list)
    changed_pages: int = 0
    overall_similarity: float = 1.0

    def to_dict(self) -> dict:
        return {
            "docx_a": str(self.docx_a),
            "docx_b": str(self.docx_b),
            "status": self.status,
            "pages_a": self.pages_a,
            "pages_b": self.pages_b,
            "changed_pages": self.changed_pages,
            "overall_similarity": round(self.overall_similarity, 4),
            "page_results": [
                {
                    "page": r.page,
                    "similarity": round(r.similarity, 4),
                    "changed": r.changed,
                    "diff_png": str(r.diff_png_path) if r.diff_png_path else None,
                }
                for r in self.page_results
            ],
        }


def _compare_pages(
    png_a: Path,
    png_b: Path,
    diff_path: Path,
    *,
    change_threshold: float = 0.995,
) -> DiffPageResult:
    """Compare two page PNGs and produce a diff image."""
    img_a = np.array(Image.open(png_a).convert("RGB"))
    img_b = np.array(Image.open(png_b).convert("RGB"))

    # Resize if dimensions differ
    if img_a.shape != img_b.shape:
        h = max(img_a.shape[0], img_b.shape[0])
        w = max(img_a.shape[1], img_b.shape[1])
        padded_a = np.full((h, w, 3), 255, dtype=np.uint8)
        padded_b = np.full((h, w, 3), 255, dtype=np.uint8)
        padded_a[:img_a.shape[0], :img_a.shape[1]] = img_a
        padded_b[:img_b.shape[0], :img_b.shape[1]] = img_b
        img_a, img_b = padded_a, padded_b

    # Pixel-level comparison
    diff_mask = np.any(np.abs(img_a.astype(int) - img_b.astype(int)) > 10, axis=2)
    similarity = 1.0 - (diff_mask.sum() / diff_mask.size)
    changed = similarity < change_threshold

    # Create diff visualization: unchanged=gray, changed=red overlay
    diff_img = (img_a * 0.3 + img_b * 0.3).astype(np.uint8)
    diff_img[diff_mask] = [255, 50, 50]  # Red highlight

    Image.fromarray(diff_img).save(str(diff_path))

    page_num = int(png_a.stem.split("-")[-1]) if "-" in png_a.stem else 0
    return DiffPageResult(
        page=page_num,
        similarity=similarity,
        diff_png_path=diff_path,
        changed=changed,
    )


def run_diff(
    *,
    docx_a: Path,
    docx_b: Path,
    output_dir: Path,
    dpi: int = 150,
) -> DiffReport:
    """Compare two docx files visually."""
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    render_a_dir = output_dir / "render_a"
    render_b_dir = output_dir / "render_b"
    diff_dir = output_dir / "diffs"
    diff_dir.mkdir(exist_ok=True)

    # Render both documents
    report_a = render_docx_to_png(docx_a, render_a_dir, dpi=dpi)
    report_b = render_docx_to_png(docx_b, render_b_dir, dpi=dpi)

    if report_a.status != "pass":
        return DiffReport(
            docx_a=docx_a, docx_b=docx_b,
            status=f"render_failed_a: {report_a.status}",
        )
    if report_b.status != "pass":
        return DiffReport(
            docx_a=docx_a, docx_b=docx_b,
            status=f"render_failed_b: {report_b.status}",
        )

    # Compare page by page
    max_pages = max(report_a.page_count, report_b.page_count)
    page_results = []

    for i in range(max_pages):
        png_a = render_a_dir / f"page-{i + 1}.png"
        png_b = render_b_dir / f"page-{i + 1}.png"
        diff_path = diff_dir / f"diff-{i + 1}.png"

        if not png_a.exists() or not png_b.exists():
            page_results.append(DiffPageResult(
                page=i + 1, similarity=0.0, changed=True,
            ))
            continue

        result = _compare_pages(png_a, png_b, diff_path)
        page_results.append(result)

    changed_pages = sum(1 for r in page_results if r.changed)
    overall_sim = (
        sum(r.similarity for r in page_results) / len(page_results)
        if page_results else 1.0
    )

    status = "success"
    if report_a.page_count != report_b.page_count:
        status = "page_count_mismatch"

    return DiffReport(
        docx_a=docx_a, docx_b=docx_b,
        status=status,
        pages_a=report_a.page_count,
        pages_b=report_b.page_count,
        page_results=page_results,
        changed_pages=changed_pages,
        overall_similarity=overall_sim,
    )
