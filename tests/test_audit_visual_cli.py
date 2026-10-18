from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.models import VisualAuditFinding, VisualRenderReport

runner = CliRunner()


def _patch_renderer(monkeypatch, status: str) -> None:
    def render(docx_path: Path, output_dir: Path, *, dpi: int = 150) -> VisualRenderReport:
        output_dir.mkdir(parents=True, exist_ok=True)
        if status != "pass":
            return VisualRenderReport(docx_path=docx_path, output_dir=output_dir, status=status)
        png = output_dir / "page-1.png"
        Image.new("RGB", (60, 80), "white").save(png)
        return VisualRenderReport(
            docx_path=docx_path, output_dir=output_dir, status="pass", page_count=1, png_paths=[png]
        )

    monkeypatch.setattr("tools.report_scaffold_v3.visual_audit.render_docx_to_png", render)


def _audit(tmp_path: Path, *extra: str):
    docx = tmp_path / "doc.docx"
    docx.write_bytes(b"")
    return runner.invoke(
        app,
        ["officex", "audit", "visual", "--candidate-docx", str(docx), "--output-dir", str(tmp_path / "out"), *extra],
    )


def test_audit_visual_json_reports_missing_renderer_as_json(monkeypatch, tmp_path):
    _patch_renderer(monkeypatch, "renderer_unavailable")

    result = _audit(tmp_path, "--as-json")

    assert result.exit_code == 2
    assert json.loads(result.stdout)["status"] == "renderer_unavailable"


def test_audit_visual_exits_1_on_error_findings_in_both_modes(monkeypatch, tmp_path):
    _patch_renderer(monkeypatch, "pass")
    monkeypatch.setattr(
        "tools.report_scaffold_v3.visual_audit_checks.run_visual_checks",
        lambda png_paths, page_setup=None: [
            VisualAuditFinding(severity="error", code="blank-page", page=1, message="Page 1 is blank.")
        ],
    )

    as_json = _audit(tmp_path, "--as-json")
    as_text = _audit(tmp_path)

    assert as_json.exit_code == 1
    assert json.loads(as_json.stdout)["findings"][0]["code"] == "blank-page"
    assert as_text.exit_code == 1
    assert "Page 1 is blank." in as_text.stdout
