from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from tools.report_scaffold_v3 import diff_runtime
from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.models import VisualRenderReport


def _page(path: Path, *, mark: bool = False) -> Path:
    image = Image.new("RGB", (60, 80), "white")
    if mark:
        for x in range(10, 50):
            for y in range(10, 40):
                image.putpixel((x, y), (0, 0, 0))
    image.save(path)
    return path


def _fake_renderer(marked_docx_names: set[str], *, status: str = "pass"):
    """Stand-in for LibreOffice: one PNG page per docx, marked if its name is listed."""

    def render(docx_path: Path, output_dir: Path, *, dpi: int = 150) -> VisualRenderReport:
        output_dir.mkdir(parents=True, exist_ok=True)
        if status != "pass":
            return VisualRenderReport(docx_path=docx_path, output_dir=output_dir, status=status)
        png = _page(output_dir / "page-1.png", mark=docx_path.name in marked_docx_names)
        return VisualRenderReport(
            docx_path=docx_path, output_dir=output_dir, status="pass", page_count=1, png_paths=[png]
        )

    return render


def _docx_pair(tmp_path: Path) -> tuple[Path, Path]:
    a, b = tmp_path / "a.docx", tmp_path / "b.docx"
    a.write_bytes(b"")
    b.write_bytes(b"")
    return a, b


def test_compare_pages_returns_plain_python_types(tmp_path):
    same = diff_runtime._compare_pages(
        _page(tmp_path / "a-1.png"), _page(tmp_path / "b-1.png"), tmp_path / "diff-1.png"
    )
    changed = diff_runtime._compare_pages(
        _page(tmp_path / "c-1.png"), _page(tmp_path / "d-1.png", mark=True), tmp_path / "diff-2.png"
    )

    assert type(same.similarity) is float and type(same.changed) is bool
    assert same.similarity == 1.0 and same.changed is False
    assert changed.changed is True and changed.similarity < 1.0
    assert (tmp_path / "diff-2.png").exists()


def test_run_diff_report_is_json_serializable(monkeypatch, tmp_path):
    monkeypatch.setattr(diff_runtime, "render_docx_to_png", _fake_renderer({"b.docx"}))
    a, b = _docx_pair(tmp_path)

    report = diff_runtime.run_diff(docx_a=a, docx_b=b, output_dir=tmp_path / "out")
    payload = json.loads(json.dumps(report.to_dict()))

    assert payload["status"] == "success"
    assert payload["changed_pages"] == 1
    assert payload["page_results"][0]["changed"] is True
    assert payload["error"] is None


def test_run_diff_render_failure_is_not_reported_as_identical(monkeypatch, tmp_path):
    monkeypatch.setattr(diff_runtime, "render_docx_to_png", _fake_renderer(set(), status="renderer_unavailable"))
    a, b = _docx_pair(tmp_path)

    report = diff_runtime.run_diff(docx_a=a, docx_b=b, output_dir=tmp_path / "out")

    assert report.render_failed
    assert report.to_dict()["overall_similarity"] is None
    assert "LibreOffice" in report.error


def test_officex_diff_cli_exit_codes(monkeypatch, tmp_path):
    runner = CliRunner()
    a, b = _docx_pair(tmp_path)
    args = ["officex", "diff", "--a", str(a), "--b", str(b), "--output-dir", str(tmp_path / "out")]

    monkeypatch.setattr(diff_runtime, "render_docx_to_png", _fake_renderer(set()))
    identical = runner.invoke(app, [*args, "--as-json"])
    assert identical.exit_code == 0, identical.output
    assert json.loads(identical.stdout)["changed_pages"] == 0

    monkeypatch.setattr(diff_runtime, "render_docx_to_png", _fake_renderer({"b.docx"}))
    changed_json = runner.invoke(app, [*args, "--as-json"])
    changed_text = runner.invoke(app, args)
    assert changed_json.exit_code == 1
    assert json.loads(changed_json.stdout)["changed_pages"] == 1
    assert changed_text.exit_code == 1
    assert "Changed pages: 1" in changed_text.stdout

    monkeypatch.setattr(diff_runtime, "render_docx_to_png", _fake_renderer(set(), status="renderer_unavailable"))
    no_renderer = runner.invoke(app, args)
    assert no_renderer.exit_code == 2
    assert "LibreOffice" in no_renderer.stdout
    assert "Changed pages" not in no_renderer.stdout
