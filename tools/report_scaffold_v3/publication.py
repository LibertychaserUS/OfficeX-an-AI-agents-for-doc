from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import PublishedRunManifest


class PublicationError(ValueError):
    pass


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_published_run_manifest(*, run_dir: Path, canonical_root: Path) -> PublishedRunManifest:
    summary_path = run_dir / "section_pipeline_summary.json"
    candidate_audit_path = run_dir / "candidate_audit.json"
    validation_path = run_dir / "validation.json"
    if not summary_path.exists():
        raise PublicationError(f"Run directory is missing `section_pipeline_summary.json`: `{summary_path}`.")
    if not candidate_audit_path.exists():
        raise PublicationError(f"Run directory is missing `candidate_audit.json`: `{candidate_audit_path}`.")
    if not validation_path.exists():
        raise PublicationError(f"Run directory is missing `validation.json`: `{validation_path}`.")

    summary = _load_json(summary_path)
    output_docx = Path(summary["output_docx"]).expanduser().resolve()
    build_source_path = Path(summary["build_source_path"]).expanduser().resolve()
    candidate_audit_markdown = Path(summary["candidate_audit_path"]).expanduser().resolve()
    validation_report_markdown = Path(summary["validation_report_path"]).expanduser().resolve()

    for required_path in (
        output_docx,
        build_source_path,
        candidate_audit_markdown,
        validation_report_markdown,
    ):
        if not required_path.exists():
            raise PublicationError(f"Run directory references a missing required artifact: `{required_path}`.")

    candidate_error_count = int(summary["candidate_error_count"])
    candidate_warning_count = int(summary["candidate_warning_count"])
    validation_error_count = int(summary["validation_error_count"])
    validation_warning_count = int(summary["validation_warning_count"])

    if candidate_error_count or validation_error_count:
        raise PublicationError("Cannot publish a run with candidate or validation errors.")
    if candidate_warning_count or validation_warning_count:
        raise PublicationError("Cannot publish a run with candidate or validation warnings.")

    published_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    published_id = f"{run_dir.name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    return PublishedRunManifest(
        published_id=published_id,
        published_at_utc=published_at,
        run_dir=run_dir,
        canonical_root=canonical_root,
        build_source_path=build_source_path,
        output_docx=output_docx,
        candidate_audit_path=candidate_audit_markdown,
        validation_report_path=validation_report_markdown,
        candidate_error_count=candidate_error_count,
        candidate_warning_count=candidate_warning_count,
        validation_error_count=validation_error_count,
        validation_warning_count=validation_warning_count,
    )


def render_published_run_markdown(manifest: PublishedRunManifest) -> str:
    return "\n".join(
        [
            "# Published Run",
            "",
            f"- Published id: `{manifest.published_id}`",
            f"- Published at (UTC): `{manifest.published_at_utc}`",
            f"- Run dir: `{manifest.run_dir}`",
            f"- Canonical root: `{manifest.canonical_root}`",
            f"- Build source: `{manifest.build_source_path}`",
            f"- Output docx: `{manifest.output_docx}`",
            f"- Candidate audit: `{manifest.candidate_audit_path}`",
            f"- Validation report: `{manifest.validation_report_path}`",
            f"- Candidate errors/warnings: {manifest.candidate_error_count}/{manifest.candidate_warning_count}",
            f"- Validation errors/warnings: {manifest.validation_error_count}/{manifest.validation_warning_count}",
        ]
    )


def publish_run(
    *,
    run_dir: Path,
    published_dir: Path,
) -> PublishedRunManifest:
    published_dir.mkdir(parents=True, exist_ok=True)
    run_dir = run_dir.expanduser().resolve()
    manifest = build_published_run_manifest(run_dir=run_dir, canonical_root=run_dir)
    run_json = run_dir / "published_run.json"
    run_md = run_dir / "published_run.md"
    current_json = published_dir / "current.json"
    current_md = published_dir / "current.md"
    history_dir = published_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_json = history_dir / f"{manifest.published_id}.json"
    history_md = history_dir / f"{manifest.published_id}.md"

    payload = manifest.model_dump(mode="json")
    markdown = render_published_run_markdown(manifest)
    for path in (run_json, current_json, history_json):
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for path in (run_md, current_md, history_md):
        path.write_text(markdown.strip() + "\n", encoding="utf-8")
    return manifest
