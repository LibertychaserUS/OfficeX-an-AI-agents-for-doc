from __future__ import annotations

import json
from pathlib import Path

from .candidate_audit import build_candidate_audit, render_candidate_audit_markdown
from .docx_inspector import inspect_docx, inspect_docx_overrides
from .manifest_loader import (
    load_baseline_manifest,
    load_figures_manifest,
    load_layout_contract,
    load_sections_manifest,
    load_snippets_manifest,
    load_template_profile,
    load_write_contract,
)
from .models import SectionPipelineReport
from .ooxml_inspector import extract_effective_style_inventory
from .section_assembler import assemble_sections_manifest, write_build_source_yaml
from .validation import build_validation_report, render_validation_markdown
from .writer import build_word_candidate


def _write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def run_section_pipeline(*, pipeline_dir: Path) -> SectionPipelineReport:
    pipeline_dir.mkdir(parents=True, exist_ok=True)

    baseline = load_baseline_manifest()
    sections_manifest = load_sections_manifest()
    figures_manifest = load_figures_manifest()
    snippets_manifest = load_snippets_manifest()
    write_contract = load_write_contract()
    template_profile = load_template_profile().model_dump(mode="json")
    layout_contract = load_layout_contract().model_dump(mode="json")

    build_source = assemble_sections_manifest(
        sections_manifest,
        figures_manifest=figures_manifest,
        snippets_manifest=snippets_manifest,
    )
    build_source_path = pipeline_dir / "assembled_sections_build.yml"
    write_build_source_yaml(build_source, build_source_path)

    template_docx = (
        baseline.format_authority_docx.expanduser().resolve()
        if baseline.format_authority_docx
        else baseline.target_docx.expanduser().resolve()
    )
    output_docx = pipeline_dir / sections_manifest.output_name
    build_word_candidate(
        template_docx=template_docx,
        source=build_source,
        contract=write_contract,
        output_docx=output_docx,
    )

    candidate_report = build_candidate_audit(
        output_docx,
        build_source_path=build_source_path,
    )
    candidate_audit_path = pipeline_dir / "candidate_audit.md"
    _write_json(pipeline_dir / "candidate_audit.json", candidate_report.model_dump(mode="json"))
    _write_markdown(candidate_audit_path, render_candidate_audit_markdown(candidate_report))

    inventory = inspect_docx(output_docx)
    override_inventory = inspect_docx_overrides(output_docx)
    style_inventory = extract_effective_style_inventory(output_docx)
    validation_report = build_validation_report(
        output_docx,
        inventory,
        target_role="candidate_output",
        format_authority_docx=baseline.format_authority_docx.expanduser().resolve()
        if baseline.format_authority_docx
        else None,
        template_profile=template_profile,
        layout_contract=layout_contract,
        style_inventory=style_inventory,
        override_inventory=override_inventory,
    )
    validation_report_path = pipeline_dir / "validation_report.md"
    _write_json(pipeline_dir / "validation.json", validation_report.model_dump(mode="json"))
    _write_markdown(validation_report_path, render_validation_markdown(validation_report))

    candidate_error_count = sum(
        1 for finding in candidate_report.findings if finding.severity == "error"
    )
    candidate_warning_count = sum(
        1 for finding in candidate_report.findings if finding.severity == "warning"
    )
    validation_error_count = sum(
        1 for finding in validation_report.findings if finding.severity == "error"
    )
    validation_warning_count = sum(
        1 for finding in validation_report.findings if finding.severity == "warning"
    )

    return SectionPipelineReport(
        build_source_path=build_source_path,
        output_docx=output_docx,
        candidate_audit_path=candidate_audit_path,
        validation_report_path=validation_report_path,
        candidate_error_count=candidate_error_count,
        candidate_warning_count=candidate_warning_count,
        validation_error_count=validation_error_count,
        validation_warning_count=validation_warning_count,
    )
