from __future__ import annotations

import json
from pathlib import Path

import pytest
from docx import Document
from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.paths import MANIFESTS_DIR

runner = CliRunner()


def _validate(*args: str):
    return runner.invoke(app, ["officex", "validate", *args])


@pytest.fixture(scope="module")
def demo_docx(tmp_path_factory) -> Path:
    sandbox = tmp_path_factory.mktemp("sandbox")
    result = runner.invoke(
        app, ["officex", "task", "run-docx-mvp", "--sandbox-root", str(sandbox), "--as-json"]
    )
    assert result.exit_code == 0, result.output
    return Path(json.loads(result.stdout)["candidate_docx"])


def _write_docx(path: Path, paragraphs: list[tuple[str, str]]) -> Path:
    document = Document()
    for style, text in paragraphs:
        document.add_paragraph(text, style=style)
    document.save(str(path))
    return path


def test_validate_demo_build_runs_both_tracks(demo_docx):
    result = _validate("--docx", str(demo_docx), "--as-json")

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["profile"] == "a4_academic"
    assert payload["status"] in {"pass", "warning"}
    assert payload["structural"]["error_count"] == 0
    assert payload["structural"]["summary"]["heading_count"] > 0
    assert len(payload["semantic"]["checks_run"]) == 6
    assert "officex audit visual" in payload["not_checked"]
    assert payload["report_paths"] == {}


def test_validate_surfaces_semantic_findings(tmp_path):
    docx = _write_docx(
        tmp_path / "citations.docx",
        [
            ("Heading 1", "Introduction"),
            ("Normal", "As shown by (Smith, 2024) and (Jones, 2023), the results hold."),
            ("Heading 1", "References"),
            ("Normal", "Smith, J. (2024) A Study of Things. Journal of Stuff."),
        ],
    )

    result = _validate("--docx", str(docx), "--as-json")

    payload = json.loads(result.stdout)
    semantic_messages = [finding["message"] for finding in payload["semantic"]["findings"]]
    assert any("Jones" in message for message in semantic_messages)
    assert not any("Smith" in message for message in semantic_messages)
    assert payload["semantic"]["warning_count"] >= 1
    assert payload["status"] != "pass"


def test_validate_exits_1_on_structural_error(tmp_path):
    docx = _write_docx(tmp_path / "no_headings.docx", [("Normal", "Just one paragraph.")])

    result = _validate("--docx", str(docx))

    assert result.exit_code == 1
    assert "FAIL" in result.stdout
    assert "missing-headings" in result.stdout


def test_validate_profile_option_does_not_activate_profile(demo_docx):
    active_manifest = MANIFESTS_DIR / "template_profile.yml"
    before = active_manifest.read_bytes()

    result = _validate("--docx", str(demo_docx), "--profile", "letter_business", "--as-json")

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["profile"] == "letter_business"
    assert active_manifest.read_bytes() == before


def test_validate_rejects_unknown_profile(demo_docx):
    result = _validate("--docx", str(demo_docx), "--profile", "nope")

    assert result.exit_code == 2
    assert "Profile `nope` not found" in result.stdout


def test_validate_output_dir_writes_reports(demo_docx, tmp_path):
    result = _validate("--docx", str(demo_docx), "--output-dir", str(tmp_path / "reports"), "--as-json")

    assert result.exit_code == 0, result.output
    report_paths = json.loads(result.stdout)["report_paths"]
    assert set(report_paths) == {"structural_json", "structural_markdown", "semantic_json", "summary_json"}
    for path in report_paths.values():
        assert Path(path).is_file()
    summary = json.loads(Path(report_paths["summary_json"]).read_text(encoding="utf-8"))
    assert summary["report_paths"] == report_paths
