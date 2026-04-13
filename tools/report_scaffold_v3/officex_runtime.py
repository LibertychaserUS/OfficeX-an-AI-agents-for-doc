from __future__ import annotations

import shutil
from pathlib import Path

from .candidate_audit import build_candidate_audit, render_candidate_audit_markdown
from .docx_inspector import inspect_docx, inspect_docx_overrides
from .manifest_loader import (
    load_baseline_manifest,
    load_build_source,
    load_layout_contract,
    load_template_profile,
    load_write_contract,
)
from .models import (
    OfficeXDocxMvpRunReport,
    OfficeXSandboxManifest,
    OfficeXStageReview,
    OfficeXTaskPacket,
)
from .ooxml_inspector import extract_effective_style_inventory
from .paths import SANDBOXES_DIR
from .runtime_common import (
    create_runtime_tree,
    local_now_iso,
    make_local_runtime_identifier,
    sanitize_runtime_identifier,
    write_runtime_json,
    write_runtime_markdown,
    write_runtime_manifest_pair,
    write_runtime_yaml,
)
from .task_runtime import load_task_packet, render_task_packet_markdown, resolve_task_packet_path
from .validation import build_validation_report, render_validation_markdown
from .writer import build_word_candidate


def render_sandbox_manifest_markdown(manifest: OfficeXSandboxManifest) -> str:
    return "\n".join(
        [
            "# OfficeX Sandbox Manifest",
            "",
            f"- Run ID: `{manifest.run_id}`",
            f"- Sandbox root: `{manifest.sandbox_root}`",
            f"- Runtime dir: `{manifest.runtime_dir}`",
            f"- Input dir: `{manifest.input_dir}`",
            f"- Candidate dir: `{manifest.candidate_dir}`",
            f"- Reports dir: `{manifest.reports_dir}`",
            f"- Source reference docx: `{manifest.source_reference_docx}`",
            f"- Mutable template docx: `{manifest.mutable_template_docx}`",
            f"- Created at: `{manifest.created_at}`",
        ]
    )


def render_stage_history_review_markdown(stages: list[OfficeXStageReview]) -> str:
    lines = ["# OfficeX Stage History Review", ""]
    for stage in stages:
        lines.append(f"## {stage.stage_id}")
        lines.append("")
        lines.append(f"- Status: `{stage.status}`")
        lines.append(f"- History check: {stage.history_check}")
        if stage.outputs:
            lines.append("- Outputs:")
            for output in stage.outputs:
                lines.append(f"  - `{output}`")
        if stage.notes:
            lines.append("- Notes:")
            for note in stage.notes:
                lines.append(f"  - {note}")
        lines.append("")
    return "\n".join(lines)


def render_run_event_log_markdown(events: list[dict]) -> str:
    lines = ["# OfficeX Run Event Log", ""]
    for event in events:
        lines.extend(
            [
                f"## {event['event_id']}",
                "",
                f"- Stage: `{event['stage_id']}`",
                f"- Status: `{event['status']}`",
                f"- Recorded at: `{event['recorded_at']}`",
            ]
        )
        if event["artifacts"]:
            lines.append("- Artifacts:")
            for artifact in event["artifacts"]:
                lines.append(f"  - `{artifact}`")
        if event["notes"]:
            lines.append("- Notes:")
            for note in event["notes"]:
                lines.append(f"  - {note}")
        lines.append("")
    return "\n".join(lines)


def render_officex_run_summary(report: OfficeXDocxMvpRunReport) -> str:
    return "\n".join(
        [
            "# OfficeX `docx` MVP Run Summary",
            "",
            f"- Run ID: `{report.run_id}`",
            f"- Sandbox root: `{report.sandbox_root}`",
            f"- Candidate docx: `{report.candidate_docx}`",
            f"- Task packet: `{report.task_packet_path}`",
            f"- Sandbox manifest: `{report.sandbox_manifest_path}`",
            f"- Build source: `{report.build_source_path}`",
            f"- Validation report: `{report.validation_report_path}`",
            f"- Candidate audit: `{report.candidate_audit_path}`",
            f"- Stage history review: `{report.stage_history_review_path}`",
            f"- Candidate errors: {report.candidate_error_count}",
            f"- Candidate warnings: {report.candidate_warning_count}",
            f"- Validation errors: {report.validation_error_count}",
            f"- Validation warnings: {report.validation_warning_count}",
        ]
    )


def _build_docx_mvp_task_packet(
    *,
    sandbox: OfficeXSandboxManifest,
    source_path: Path,
    baseline_target_docx: Path,
    baseline_manifest_path: Path,
    write_contract_path: Path,
    approval_mode: str,
) -> OfficeXTaskPacket:
    return OfficeXTaskPacket(
        task_packet_id=f"{sandbox.run_id}-task",
        goal="Run the OfficeX docx MVP deterministic generation and audit loop inside a sandbox.",
        task_family="document_generation",
        active_workspace=sandbox.sandbox_root,
        allowed_surfaces=[
            str(sandbox.runtime_dir),
            str(sandbox.candidate_dir),
            str(sandbox.reports_dir),
        ],
        blocked_surfaces=[
            str(baseline_target_docx),
            "/Users/nihao/Documents/Playground/archive/products/loopmart",
        ],
        input_artifacts=[
            sandbox.source_reference_docx,
            source_path.expanduser().resolve(),
            baseline_manifest_path.expanduser().resolve(),
            write_contract_path.expanduser().resolve(),
        ],
        constraints=[
            "Use sandbox copies only for mutable output.",
            "Treat docx structure, styles, numbering, and layout as deterministic program outputs.",
            "Do not publish as a side effect.",
            "Write a stage history review for this run.",
        ],
        approval_mode=approval_mode,
        acceptance_gates=[
            "Candidate docx exists in the sandbox candidate directory.",
            "Validation report is written.",
            "Candidate audit report is written.",
            "Stage history review is written.",
        ],
        publish_gate="never_publish",
        expected_outputs=[
            "sandbox candidate docx",
            "validation report",
            "candidate audit report",
            "stage history review",
        ],
    )


def _build_docx_mvp_stage_reviews(
    *,
    sandbox: OfficeXSandboxManifest,
    task_packet_path: Path,
    output_docx: Path,
    validation_report_path: Path,
    candidate_audit_path: Path,
) -> list[OfficeXStageReview]:
    return [
        OfficeXStageReview(
            stage_id="sandbox_created",
            history_check="Mutable work was isolated from imported references and archived workspaces.",
            outputs=[str(sandbox.sandbox_root), str(sandbox.runtime_dir / "sandbox_manifest.json")],
        ),
        OfficeXStageReview(
            stage_id="task_packet_written",
            history_check="This run was governed by a structured task packet rather than a loose prompt.",
            outputs=[str(task_packet_path)],
        ),
        OfficeXStageReview(
            stage_id="baseline_copied",
            history_check="The source template was copied into the sandbox before any deterministic mutation.",
            outputs=[str(sandbox.mutable_template_docx), str(sandbox.reports_dir / "baseline_inventory.json")],
        ),
        OfficeXStageReview(
            stage_id="candidate_built",
            history_check="The candidate was produced through deterministic docx build logic, not direct editor mutation.",
            outputs=[str(output_docx), str(sandbox.reports_dir / "build_summary.json")],
        ),
        OfficeXStageReview(
            stage_id="candidate_validated",
            history_check="Validation captured structured findings against the active OfficeX template and layout contracts.",
            outputs=[str(sandbox.reports_dir / "validation.json"), str(validation_report_path)],
        ),
        OfficeXStageReview(
            stage_id="candidate_audited",
            history_check="Candidate audit checked the generated docx against the build source and write contract.",
            outputs=[str(sandbox.reports_dir / "candidate_audit.json"), str(candidate_audit_path)],
        ),
    ]


def _build_docx_mvp_run_events(stages: list[OfficeXStageReview]) -> list[dict]:
    events: list[dict] = []
    for index, stage in enumerate(stages, start=1):
        events.append(
            {
                "event_id": f"event-{index:02d}",
                "stage_id": stage.stage_id,
                "status": stage.status,
                "recorded_at": local_now_iso(),
                "artifacts": list(stage.outputs),
                "notes": list(stage.notes),
            }
        )
    return events


def _count_findings_by_severity(findings, severity: str) -> int:
    return sum(1 for finding in findings if finding.severity == severity)


def create_docx_mvp_sandbox(
    *,
    run_id: str | None = None,
    sandbox_root: Path = SANDBOXES_DIR,
    baseline_manifest_path: Path,
) -> OfficeXSandboxManifest:
    baseline = load_baseline_manifest(baseline_manifest_path)
    resolved_root = sandbox_root.expanduser().resolve()
    final_run_id = sanitize_runtime_identifier(
        run_id or make_local_runtime_identifier("officex-docx-mvp"),
        fallback="officex-docx-mvp",
    )
    sandbox_dir = resolved_root / final_run_id
    if sandbox_dir.exists():
        raise FileExistsError(f"Sandbox already exists: {sandbox_dir}")

    created = create_runtime_tree(
        sandbox_dir,
        "runtime",
        "input",
        "candidate",
        "reports",
    )
    runtime_dir = created["runtime"]
    input_dir = created["input"]
    candidate_dir = created["candidate"]
    reports_dir = created["reports"]

    source_reference = baseline.target_docx.expanduser().resolve()
    mutable_template = input_dir / source_reference.name
    shutil.copy2(source_reference, mutable_template)

    manifest = OfficeXSandboxManifest(
        run_id=final_run_id,
        sandbox_root=sandbox_dir,
        runtime_dir=runtime_dir,
        input_dir=input_dir,
        candidate_dir=candidate_dir,
        reports_dir=reports_dir,
        source_reference_docx=source_reference,
        mutable_template_docx=mutable_template,
        created_at=local_now_iso(),
    )
    write_runtime_manifest_pair(
        runtime_dir,
        stem="sandbox_manifest",
        payload=manifest.model_dump(mode="json"),
        markdown=render_sandbox_manifest_markdown(manifest),
    )
    return manifest


def run_docx_mvp(
    *,
    run_id: str | None = None,
    sandbox_root: Path = SANDBOXES_DIR,
    source_path: Path,
    baseline_manifest_path: Path,
    write_contract_path: Path,
    approval_mode: str,
) -> OfficeXDocxMvpRunReport:
    baseline = load_baseline_manifest(baseline_manifest_path)
    sandbox = create_docx_mvp_sandbox(
        run_id=run_id,
        sandbox_root=sandbox_root,
        baseline_manifest_path=baseline_manifest_path,
    )

    build_source = load_build_source(source_path.expanduser().resolve())
    write_contract = load_write_contract(write_contract_path.expanduser().resolve())
    template_profile = load_template_profile().model_dump(mode="json")
    layout_contract = load_layout_contract().model_dump(mode="json")

    build_source_path = sandbox.runtime_dir / "build_source.yml"
    write_runtime_yaml(build_source_path, build_source.model_dump(mode="json"))

    task_packet = _build_docx_mvp_task_packet(
        sandbox=sandbox,
        source_path=source_path,
        baseline_target_docx=baseline.target_docx.expanduser().resolve(),
        baseline_manifest_path=baseline_manifest_path,
        write_contract_path=write_contract_path,
        approval_mode=approval_mode,
    )
    task_packet_path = sandbox.runtime_dir / "task_packet.json"
    write_runtime_manifest_pair(
        sandbox.runtime_dir,
        stem="task_packet",
        payload=task_packet.model_dump(mode="json"),
        markdown=render_task_packet_markdown(task_packet),
    )

    inventory = inspect_docx(sandbox.mutable_template_docx)
    write_runtime_json(sandbox.reports_dir / "baseline_inventory.json", inventory)

    output_docx = sandbox.candidate_dir / build_source.output_name
    build_result = build_word_candidate(
        template_docx=sandbox.mutable_template_docx,
        source=build_source,
        contract=write_contract,
        output_docx=output_docx,
    )
    write_runtime_json(
        sandbox.reports_dir / "build_summary.json",
        build_result.model_dump(mode="json"),
    )

    candidate_report = build_candidate_audit(
        output_docx,
        build_source_path=build_source_path,
        write_contract_path=write_contract_path.expanduser().resolve(),
    )
    candidate_audit_path = sandbox.reports_dir / "candidate_audit.md"
    write_runtime_json(
        sandbox.reports_dir / "candidate_audit.json",
        candidate_report.model_dump(mode="json"),
    )
    write_runtime_markdown(candidate_audit_path, render_candidate_audit_markdown(candidate_report))

    candidate_inventory = inspect_docx(output_docx)
    override_inventory = inspect_docx_overrides(output_docx)
    style_inventory = extract_effective_style_inventory(output_docx)
    validation_report = build_validation_report(
        output_docx,
        candidate_inventory,
        target_role="candidate_output",
        format_authority_docx=sandbox.mutable_template_docx,
        template_profile=template_profile,
        layout_contract=layout_contract,
        style_inventory=style_inventory,
        override_inventory=override_inventory,
    )
    validation_report_path = sandbox.reports_dir / "validation_report.md"
    write_runtime_json(
        sandbox.reports_dir / "validation.json",
        validation_report.model_dump(mode="json"),
    )
    write_runtime_markdown(validation_report_path, render_validation_markdown(validation_report))

    stage_reviews = _build_docx_mvp_stage_reviews(
        sandbox=sandbox,
        task_packet_path=task_packet_path,
        output_docx=output_docx,
        validation_report_path=validation_report_path,
        candidate_audit_path=candidate_audit_path,
    )
    stage_history_review_path = sandbox.reports_dir / "stage_history_review.md"
    write_runtime_json(
        sandbox.reports_dir / "stage_history_review.json",
        [stage.model_dump(mode="json") for stage in stage_reviews],
    )
    write_runtime_markdown(stage_history_review_path, render_stage_history_review_markdown(stage_reviews))
    run_events = _build_docx_mvp_run_events(stage_reviews)
    write_runtime_json(sandbox.reports_dir / "run_event_log.json", run_events)
    write_runtime_markdown(
        sandbox.reports_dir / "run_event_log.md",
        render_run_event_log_markdown(run_events),
    )

    candidate_error_count = _count_findings_by_severity(candidate_report.findings, "error")
    candidate_warning_count = _count_findings_by_severity(candidate_report.findings, "warning")
    validation_error_count = _count_findings_by_severity(validation_report.findings, "error")
    validation_warning_count = _count_findings_by_severity(
        validation_report.findings, "warning"
    )

    report = OfficeXDocxMvpRunReport(
        run_id=sandbox.run_id,
        sandbox_root=sandbox.sandbox_root,
        task_packet_path=task_packet_path,
        sandbox_manifest_path=sandbox.runtime_dir / "sandbox_manifest.json",
        build_source_path=build_source_path,
        candidate_docx=output_docx,
        validation_report_path=validation_report_path,
        candidate_audit_path=candidate_audit_path,
        stage_history_review_path=stage_history_review_path,
        candidate_error_count=candidate_error_count,
        candidate_warning_count=candidate_warning_count,
        validation_error_count=validation_error_count,
        validation_warning_count=validation_warning_count,
    )
    write_runtime_json(sandbox.reports_dir / "run_summary.json", report.model_dump(mode="json"))
    write_runtime_markdown(sandbox.reports_dir / "run_summary.md", render_officex_run_summary(report))
    return report
