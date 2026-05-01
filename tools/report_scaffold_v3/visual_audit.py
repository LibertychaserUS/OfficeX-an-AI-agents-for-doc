"""Visual audit renderer: docx -> PDF -> per-page PNG.

Uses LibreOffice headless for docx->PDF conversion, then pymupdf (fitz)
for PDF->PNG page extraction.  Falls back gracefully when LibreOffice
is unavailable (status="renderer_unavailable").

Aligned with CodeX document skill render_docx.py strategy:
- Isolated LibreOffice profile to avoid lock conflicts
- Temporary working directory for conversion
- Verbose error reporting
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from .models import VisualRenderReport

logger = logging.getLogger(__name__)

_SOFFICE_NAMES = ("soffice", "libreoffice")
_MACOS_SOFFICE_PATHS = (
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/opt/homebrew/bin/soffice",
)


def _find_soffice() -> str | None:
    """Locate the soffice binary."""
    for name in _SOFFICE_NAMES:
        path = shutil.which(name)
        if path:
            return path
    for path in _MACOS_SOFFICE_PATHS:
        if Path(path).is_file():
            return path
    return None


def _get_soffice_version(soffice: str) -> str:
    try:
        result = subprocess.run(
            [soffice, "--version"],
            capture_output=True, text=True, timeout=15,
        )
        return result.stdout.strip().split("\n")[0] if result.returncode == 0 else ""
    except Exception:
        return ""


def _convert_docx_to_pdf(
    soffice: str,
    docx_path: Path,
    work_dir: Path,
) -> Path | None:
    """Convert docx to PDF using LibreOffice headless."""
    profile_dir = work_dir / "lo_profile"
    profile_dir.mkdir(exist_ok=True)

    cmd = [
        soffice,
        "--headless",
        "--norestore",
        f"-env:UserInstallation=file://{profile_dir}",
        "--convert-to", "pdf",
        "--outdir", str(work_dir),
        str(docx_path),
    ]

    logger.debug("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        logger.error("LibreOffice conversion timed out after 120s")
        return None

    if result.returncode != 0:
        logger.error("soffice exited %d: %s", result.returncode, result.stderr)
        return None

    pdf_name = docx_path.stem + ".pdf"
    pdf_path = work_dir / pdf_name
    if not pdf_path.exists():
        logger.error("Expected PDF not found at %s", pdf_path)
        return None

    return pdf_path


def _pdf_to_pngs(
    pdf_path: Path,
    output_dir: Path,
    *,
    dpi: int = 150,
) -> list[Path]:
    """Split PDF into per-page PNGs using pymupdf."""
    import fitz  # pymupdf

    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    png_paths: list[Path] = []

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=matrix)
        png_path = output_dir / f"page-{page_num + 1}.png"
        pix.save(str(png_path))
        png_paths.append(png_path)
        logger.debug("Rendered page %d -> %s (%dx%d)", page_num + 1, png_path, pix.width, pix.height)

    doc.close()
    return png_paths


def render_docx_to_png(
    docx_path: Path,
    output_dir: Path,
    *,
    dpi: int = 150,
) -> VisualRenderReport:
    """Render a docx to per-page PNG images.

    Returns a VisualRenderReport with status:
    - "pass": rendering succeeded
    - "renderer_unavailable": LibreOffice not found
    - "render_failed": conversion or PNG extraction failed
    """
    docx_path = docx_path.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    soffice = _find_soffice()
    if soffice is None:
        logger.debug("LibreOffice (soffice) not found; visual audit unavailable")
        return VisualRenderReport(
            docx_path=docx_path,
            output_dir=output_dir,
            status="renderer_unavailable",
        )

    version = _get_soffice_version(soffice)

    with tempfile.TemporaryDirectory(prefix="officex_visual_") as work_dir:
        work_path = Path(work_dir)
        pdf_path = _convert_docx_to_pdf(soffice, docx_path, work_path)

        if pdf_path is None:
            return VisualRenderReport(
                docx_path=docx_path,
                output_dir=output_dir,
                status="render_failed",
                renderer_name="LibreOffice",
                renderer_version=version,
            )

        try:
            png_paths = _pdf_to_pngs(pdf_path, output_dir, dpi=dpi)
        except Exception as exc:
            logger.error("PDF to PNG conversion failed: %s", exc)
            return VisualRenderReport(
                docx_path=docx_path,
                output_dir=output_dir,
                status="render_failed",
                renderer_name="LibreOffice",
                renderer_version=version,
            )

    return VisualRenderReport(
        docx_path=docx_path,
        output_dir=output_dir,
        status="pass",
        page_count=len(png_paths),
        png_paths=png_paths,
        renderer_name="LibreOffice",
        renderer_version=version,
    )
