from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

import yaml

from .officex_runtime import run_docx_mvp
from .paths import DEFAULT_BASELINE_MANIFEST, DEFAULT_WRITE_CONTRACT_MANIFEST
from .product_common import default_machine_settings_dir, detect_word_app, read_macos_app_version
from .product_models import (
    OfficeXCheckStatus,
    OfficeXRenderBoundaryReport,
    OfficeXRenderBoundaryScenario,
    OfficeXRendererEnvironmentProfile,
)
from .runtime_common import (
    local_now_iso,
    sanitize_runtime_identifier,
    write_runtime_json,
    write_runtime_markdown,
)


def _make_report_id(prefix: str) -> str:
    return sanitize_runtime_identifier(
        f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}",
        fallback=prefix,
    )


def _render_boundary_report_root(settings_dir: Path) -> Path:
    return settings_dir / "reports" / "render-boundary"


def render_boundary_latest_report_json_path(settings_dir: Path) -> Path:
    return _render_boundary_report_root(settings_dir) / "latest.json"


def render_boundary_latest_report_markdown_path(settings_dir: Path) -> Path:
    return _render_boundary_report_root(settings_dir) / "latest.md"


def _paragraph_text(profile_id: str, section_index: int, paragraph_index: int, repeat: int) -> str:
    seed = (
        f"OfficeX {profile_id} paragraph {section_index}.{paragraph_index} "
        "tests deterministic generation, bounded mutation, audit integrity, "
        "and render-boundary reporting under sustained document load."
    )
    return " ".join(seed for _ in range(repeat))


def _build_source_payload(
    *,
    profile_id: str,
    section_count: int,
    paragraphs_per_section: int,
    sentence_repeat: int,
) -> dict:
    blocks: list[dict] = [
        {
            "kind": "paragraph",
            "role": "heading_1",
            "text": f"OfficeX {profile_id.title()} Render Boundary",
        }
    ]
    for section_index in range(1, section_count + 1):
        blocks.append(
            {
                "kind": "paragraph",
                "role": "heading_2",
                "text": f"Section {section_index} - {profile_id.title()} Coverage",
            }
        )
        for paragraph_index in range(1, paragraphs_per_section + 1):
            role = "indented_body" if paragraph_index % 4 == 0 else "body"
            blocks.append(
                {
                    "kind": "paragraph",
                    "role": role,
                    "text": _paragraph_text(
                        profile_id,
                        section_index,
                        paragraph_index,
                        sentence_repeat,
                    ),
                }
            )
    blocks.extend(
        [
            {
                "kind": "paragraph",
                "role": "heading_2",
                "text": "Appendix - Platform Placeholder",
            },
            {
                "kind": "paragraph",
                "role": "body",
                "text": "Appendix placeholder used by the OfficeX render-boundary benchmark.",
            },
        ]
    )
    return {
        "schema_version": 1,
        "document_id": f"officex-render-boundary-{profile_id}",
        "output_name": f"officex_render_boundary_{profile_id}.docx",
        "blocks": blocks,
    }


def _write_build_source(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def collect_length_profile_results(
    *,
    build_sources_dir: Path,
    benchmark_root: Path,
) -> list[dict]:
    scenario_specs = [
        ("short-plain", "short", "plain_text", "replace_text", 2, 2, 1),
        ("medium-headings", "medium", "heading_numbering", "insert_paragraph", 4, 5, 2),
        ("long-code", "long", "code_block", "restyle", 8, 8, 3),
        ("ultra-long-headings", "ultra_long", "heading_numbering", "replace_text", 16, 12, 4),
    ]
    results: list[dict] = []
    build_sources_dir.mkdir(parents=True, exist_ok=True)
    benchmark_root.mkdir(parents=True, exist_ok=True)
    for scenario_id, document_length, structure_profile, operation_profile, section_count, paragraphs_per_section, sentence_repeat in scenario_specs:
        payload = _build_source_payload(
            profile_id=scenario_id,
            section_count=section_count,
            paragraphs_per_section=paragraphs_per_section,
            sentence_repeat=sentence_repeat,
        )
        source_path = _write_build_source(build_sources_dir / f"{scenario_id}.yml", payload)
        run_report = run_docx_mvp(
            run_id=scenario_id,
            sandbox_root=benchmark_root,
            source_path=source_path,
            baseline_manifest_path=DEFAULT_BASELINE_MANIFEST,
            write_contract_path=DEFAULT_WRITE_CONTRACT_MANIFEST,
            approval_mode="ask_every_conflict",
        )
        if run_report.validation_error_count > 0 or run_report.candidate_error_count > 0:
            status = "fail"
            requires_human_review = True
            localization_confidence = 0.0
            patch_confidence = 0.0
            notes = ["Scenario failed deterministic generation or validation."]
        elif document_length in {"long", "ultra_long"}:
            status = "warning"
            requires_human_review = True
            localization_confidence = 0.8 if document_length == "long" else 0.72
            patch_confidence = 0.78 if document_length == "long" else 0.7
            notes = ["Manual review is still advised for long-document environments."]
        else:
            status = "pass"
            requires_human_review = False
            localization_confidence = 0.95
            patch_confidence = 0.95
            notes = ["Deterministic generation completed without known runtime findings."]

        results.append(
            {
                "scenario_id": scenario_id,
                "document_length": document_length,
                "structure_profile": structure_profile,
                "operation_profile": operation_profile,
                "status": status,
                "localization_confidence": localization_confidence,
                "patch_applicability_confidence": patch_confidence,
                "requires_human_review": requires_human_review,
                "notes": notes,
            }
        )
    return results


def _capability_matrix_from_scenarios(scenarios: list[OfficeXRenderBoundaryScenario]) -> dict[str, dict[str, str]]:
    matrix: dict[str, dict[str, str]] = {
        "replace_text": {"short": "not_supported", "medium": "not_supported", "long": "not_supported", "ultra_long": "not_supported"},
        "insert_paragraph": {"short": "not_supported", "medium": "not_supported", "long": "not_supported", "ultra_long": "not_supported"},
        "restyle": {"short": "not_supported", "medium": "not_supported", "long": "not_supported", "ultra_long": "not_supported"},
        "figure_caption_repair": {"short": "not_supported", "medium": "not_supported", "long": "not_supported", "ultra_long": "not_supported"},
        "page_safe_repair": {"short": "not_supported", "medium": "not_supported", "long": "not_supported", "ultra_long": "not_supported"},
    }
    for scenario in scenarios:
        matrix.setdefault(scenario.operation_profile, {})
        matrix[scenario.operation_profile][scenario.document_length] = scenario.status
    return matrix


def build_render_boundary_report(
    *,
    workspace_root: Path,
    sandbox_root: Path,
) -> OfficeXRenderBoundaryReport:
    resolved_workspace = workspace_root.expanduser().resolve()
    resolved_sandbox = sandbox_root.expanduser().resolve()
    settings_dir = default_machine_settings_dir()
    generated_at = local_now_iso()
    report_id = _make_report_id("officex-render-boundary")
    build_sources_dir = resolved_workspace / ".officex" / "render-boundary" / report_id / "sources"
    benchmark_root = resolved_sandbox / "render-boundary" / report_id
    word_app = detect_word_app()
    renderer_profile = OfficeXRendererEnvironmentProfile(
        renderer_id="microsoft_word",
        display_name="Microsoft Word",
        detected=word_app is not None,
        app_path=word_app,
        version=read_macos_app_version(word_app),
        acceptance_role="primary",
    )

    if word_app is None:
        return OfficeXRenderBoundaryReport(
            report_id=report_id,
            generated_at=generated_at,
            overall_status="fail",
            workspace_root=resolved_workspace,
            sandbox_root=resolved_sandbox,
            machine_settings_dir=settings_dir,
            renderer_profile=renderer_profile,
            capability_matrix=_capability_matrix_from_scenarios([]),
            residual_risk_notes=[
                "Microsoft Word was not detected, so acceptance rendering cannot be verified in this environment."
            ],
            scenarios=[],
        )

    try:
        scenario_payloads = collect_length_profile_results(
            build_sources_dir=build_sources_dir,
            benchmark_root=benchmark_root,
        )
        scenarios = [OfficeXRenderBoundaryScenario.model_validate(item) for item in scenario_payloads]
        capability_matrix = _capability_matrix_from_scenarios(scenarios)

        if any(scenario.status == "fail" for scenario in scenarios):
            overall_status: OfficeXCheckStatus = "fail"
        elif any(scenario.status == "warning" for scenario in scenarios):
            overall_status = "warning"
        else:
            overall_status = "pass"

        residual_risk_notes = [
            "Table and figure-caption repair remain outside the current deterministic execution subset.",
            "Long and ultra-long documents still require explicit manual review for final Word acceptance.",
        ]
    except Exception as exc:  # pragma: no cover - defensive boundary
        scenarios = []
        capability_matrix = _capability_matrix_from_scenarios([])
        overall_status = "fail"
        residual_risk_notes = [
            f"Render-boundary execution failed before scenario completion: {exc}",
        ]

    return OfficeXRenderBoundaryReport(
        report_id=report_id,
        generated_at=generated_at,
        overall_status=overall_status,
        workspace_root=resolved_workspace,
        sandbox_root=resolved_sandbox,
        machine_settings_dir=settings_dir,
        renderer_profile=renderer_profile,
        capability_matrix=capability_matrix,
        residual_risk_notes=residual_risk_notes,
        source_fixture_dir=build_sources_dir,
        benchmark_run_root=benchmark_root,
        scenarios=scenarios,
    )


def persist_render_boundary_report(
    report: OfficeXRenderBoundaryReport,
) -> OfficeXRenderBoundaryReport:
    if report.machine_settings_dir is None:
        raise ValueError("machine_settings_dir is required to persist render-boundary reports.")

    report_root = _render_boundary_report_root(report.machine_settings_dir)
    archive_dir = report_root / report.report_id
    archive_dir.mkdir(parents=True, exist_ok=True)

    json_path = archive_dir / "render_boundary_report.json"
    markdown_path = archive_dir / "render_boundary_report.md"
    persisted_report = report.model_copy(
        update={
            "report_json_path": json_path,
            "report_markdown_path": markdown_path,
        }
    )
    write_runtime_json(json_path, persisted_report.model_dump(mode="json"))
    write_runtime_markdown(markdown_path, render_render_boundary_markdown(persisted_report))
    shutil.copyfile(json_path, render_boundary_latest_report_json_path(report.machine_settings_dir))
    shutil.copyfile(
        markdown_path,
        render_boundary_latest_report_markdown_path(report.machine_settings_dir),
    )
    return persisted_report


def render_render_boundary_markdown(report: OfficeXRenderBoundaryReport) -> str:
    lines = [
        "# OfficeX Render Boundary Report",
        "",
        f"- Report id: `{report.report_id}`",
        f"- Generated at: `{report.generated_at}`",
        f"- Overall status: `{report.overall_status}`",
        f"- Workspace root: `{report.workspace_root}`",
        f"- Sandbox root: `{report.sandbox_root}`",
        f"- Machine settings dir: `{report.machine_settings_dir}`",
        f"- Renderer: `{report.renderer_profile.display_name}`",
        f"- Renderer detected: `{report.renderer_profile.detected}`",
        f"- Renderer version: `{report.renderer_profile.version or '[unknown]'}`",
        f"- Source fixture dir: `{report.source_fixture_dir or '[not generated]'}`",
        f"- Benchmark run root: `{report.benchmark_run_root or '[not generated]'}`",
        "",
        "## Scenarios",
        "",
    ]
    if not report.scenarios:
        lines.append("- No executable scenarios were run.")
    else:
        for scenario in report.scenarios:
            lines.extend(
                [
                    f"### {scenario.scenario_id}",
                    "",
                    f"- Document length: `{scenario.document_length}`",
                    f"- Structure profile: `{scenario.structure_profile}`",
                    f"- Operation profile: `{scenario.operation_profile}`",
                    f"- Status: `{scenario.status}`",
                    f"- Localization confidence: {scenario.localization_confidence}",
                    f"- Patch applicability confidence: {scenario.patch_applicability_confidence}",
                    f"- Human review required: `{scenario.requires_human_review}`",
                ]
            )
            if scenario.notes:
                lines.append("- Notes:")
                lines.extend([f"  - {note}" for note in scenario.notes])
            lines.append("")
    if report.residual_risk_notes:
        lines.extend(["## Residual Risk Notes", ""])
        lines.extend([f"- {note}" for note in report.residual_risk_notes])
    return "\n".join(lines)
