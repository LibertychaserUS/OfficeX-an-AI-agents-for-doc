from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.report_scaffold_v3.publication import (
    PublicationError,
    build_published_run_manifest,
    publish_run,
    render_published_run_markdown,
)


def _write_required_run_artifacts(
    run_dir: Path,
    *,
    candidate_error_count: int = 0,
    candidate_warning_count: int = 0,
    validation_error_count: int = 0,
    validation_warning_count: int = 0,
) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    output_docx = run_dir / "candidate_output.docx"
    build_source_path = run_dir / "assembled.yml"
    candidate_audit_markdown = run_dir / "candidate_audit.md"
    validation_report_markdown = run_dir / "validation_report.md"
    candidate_audit_json = run_dir / "candidate_audit.json"
    validation_json = run_dir / "validation.json"

    output_docx.write_text("docx-placeholder", encoding="utf-8")
    build_source_path.write_text("schema_version: 1\n", encoding="utf-8")
    candidate_audit_markdown.write_text("# Candidate Audit\n", encoding="utf-8")
    validation_report_markdown.write_text("# Validation Report\n", encoding="utf-8")
    candidate_audit_json.write_text(json.dumps({"findings": []}), encoding="utf-8")
    validation_json.write_text(json.dumps({"findings": []}), encoding="utf-8")

    summary_payload = {
        "output_docx": str(output_docx),
        "build_source_path": str(build_source_path),
        "candidate_audit_path": str(candidate_audit_markdown),
        "validation_report_path": str(validation_report_markdown),
        "candidate_error_count": candidate_error_count,
        "candidate_warning_count": candidate_warning_count,
        "validation_error_count": validation_error_count,
        "validation_warning_count": validation_warning_count,
    }
    (run_dir / "section_pipeline_summary.json").write_text(
        json.dumps(summary_payload, indent=2),
        encoding="utf-8",
    )
    return {
        "output_docx": output_docx,
        "build_source_path": build_source_path,
        "candidate_audit_markdown": candidate_audit_markdown,
        "validation_report_markdown": validation_report_markdown,
        "candidate_audit_json": candidate_audit_json,
        "validation_json": validation_json,
        "summary_payload": summary_payload,
    }


def test_publish_run_writes_current_and_history_manifests(tmp_path: Path):
    run_dir = tmp_path / "section_pipeline"
    published_dir = tmp_path / "published"
    artifacts = _write_required_run_artifacts(run_dir)

    manifest = publish_run(run_dir=run_dir, published_dir=published_dir)

    assert manifest.run_dir == run_dir.resolve()
    assert manifest.canonical_root == run_dir.resolve()
    assert manifest.target_docx_role == "candidate_output"
    assert manifest.published_id.startswith(f"{run_dir.name}-")
    assert manifest.published_at_utc.endswith("+00:00")

    expected_payload = manifest.model_dump(mode="json")
    run_json_path = run_dir / "published_run.json"
    run_md_path = run_dir / "published_run.md"
    current_json_path = published_dir / "current.json"
    current_md_path = published_dir / "current.md"
    history_dir = published_dir / "history"
    history_json_path = history_dir / f"{manifest.published_id}.json"
    history_md_path = history_dir / f"{manifest.published_id}.md"

    assert run_json_path.exists()
    assert run_md_path.exists()
    assert current_json_path.exists()
    assert current_md_path.exists()
    assert history_json_path.exists()
    assert history_md_path.exists()

    assert json.loads(run_json_path.read_text(encoding="utf-8")) == expected_payload
    assert json.loads(current_json_path.read_text(encoding="utf-8")) == expected_payload
    assert json.loads(history_json_path.read_text(encoding="utf-8")) == expected_payload

    markdown = render_published_run_markdown(manifest)
    assert run_md_path.read_text(encoding="utf-8") == markdown.strip() + "\n"
    assert current_md_path.read_text(encoding="utf-8") == markdown.strip() + "\n"
    assert history_md_path.read_text(encoding="utf-8") == markdown.strip() + "\n"
    assert "Published Run" in markdown
    assert str(artifacts["output_docx"]) in markdown
    assert str(artifacts["build_source_path"]) in markdown


@pytest.mark.parametrize(
    ("candidate_error_count", "candidate_warning_count", "validation_error_count", "validation_warning_count", "expected_message"),
    [
        (1, 0, 0, 0, "candidate or validation errors"),
        (0, 0, 1, 0, "candidate or validation errors"),
        (0, 1, 0, 0, "candidate or validation warnings"),
        (0, 0, 0, 1, "candidate or validation warnings"),
    ],
)
def test_build_published_run_manifest_blocks_non_publishable_runs(
    tmp_path: Path,
    candidate_error_count: int,
    candidate_warning_count: int,
    validation_error_count: int,
    validation_warning_count: int,
    expected_message: str,
):
    run_dir = tmp_path / "section_pipeline"
    _write_required_run_artifacts(
        run_dir,
        candidate_error_count=candidate_error_count,
        candidate_warning_count=candidate_warning_count,
        validation_error_count=validation_error_count,
        validation_warning_count=validation_warning_count,
    )

    with pytest.raises(PublicationError, match=expected_message):
        build_published_run_manifest(run_dir=run_dir, canonical_root=run_dir)


def test_build_published_run_manifest_rejects_missing_referenced_artifacts(tmp_path: Path):
    run_dir = tmp_path / "section_pipeline"
    _write_required_run_artifacts(run_dir)
    missing_markdown = run_dir / "validation_report.md"
    missing_markdown.unlink()

    with pytest.raises(PublicationError, match="missing required artifact"):
        build_published_run_manifest(run_dir=run_dir, canonical_root=run_dir)

