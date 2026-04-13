from __future__ import annotations

from pathlib import Path

from .models import OfficeXPatchBridgeReport, OfficeXPatchBundle, OfficeXPatchOperation
from .officex_exec.common import compute_file_sha256, make_exec_id, utc_now_iso
from .officex_exec.executor import execute_officex_patch_spec, render_officex_execution_markdown
from .officex_exec.models import (
    OfficeXExecutionOperation,
    OfficeXExecutionPatchSpec,
    OfficeXExecutionPostcondition,
    OfficeXExecutionReport,
    OfficeXLiveAnchorRecord,
    OfficeXLiveAnchorSnapshot,
)
from .runtime_common import (
    ensure_mutable_candidate,
    load_runtime_structured_model,
    resolve_runtime_artifact_dir,
    write_runtime_json,
    write_runtime_markdown,
    write_runtime_yaml,
)

SUPPORTED_OPERATION_KIND_TO_ACTION = {
    "replace_text": "replace_paragraph_text",
    "insert_paragraph": "insert_paragraph_after",
    "restyle_paragraph": "update_paragraph_style",
}

SUPPORTED_EXECUTOR_KIND = {
    "replace_text": "ooxml_text_executor",
    "insert_paragraph": "ooxml_text_executor",
    "restyle_paragraph": "ooxml_style_executor",
}

SUPPORTED_SCOPE = "single_paragraph"
SUPPORTED_ANCHOR_KINDS = {"paragraph", "heading"}


def load_officex_patch_bundle(path: Path) -> OfficeXPatchBundle:
    return load_runtime_structured_model(path.expanduser().resolve(), OfficeXPatchBundle)


def load_live_anchor_snapshot(path: Path) -> OfficeXLiveAnchorSnapshot:
    return load_runtime_structured_model(path.expanduser().resolve(), OfficeXLiveAnchorSnapshot)


def _resolve_anchor(
    anchor_map: dict[str, OfficeXLiveAnchorRecord],
    operation: OfficeXPatchOperation,
) -> OfficeXLiveAnchorRecord:
    if operation.target_anchor_id not in anchor_map:
        raise ValueError(f"Missing anchor `{operation.target_anchor_id}` for OfficeX operation `{operation.operation_id}`.")
    anchor = anchor_map[operation.target_anchor_id]
    if anchor.uniqueness_status == "non_unique":
        raise ValueError(f"Anchor `{anchor.anchor_id}` is non-unique and cannot be executed.")
    if anchor.uniqueness_status == "missing":
        raise ValueError(f"Anchor `{anchor.anchor_id}` is missing and cannot be executed.")
    if anchor.block_kind not in SUPPORTED_ANCHOR_KINDS:
        raise ValueError(
            f"Unsupported anchor kind `{anchor.block_kind}` for OfficeX operation `{operation.operation_id}`."
        )
    return anchor


def _validate_operation(
    operation: OfficeXPatchOperation,
    anchor: OfficeXLiveAnchorRecord,
    *,
    approval_mode: str,
    current_candidate_hash: str,
) -> None:
    if operation.operation_kind not in SUPPORTED_OPERATION_KIND_TO_ACTION:
        raise ValueError(f"Unsupported OfficeX operation kind `{operation.operation_kind}`.")
    if operation.allowed_scope != SUPPORTED_SCOPE:
        raise ValueError(
            f"Unsupported OfficeX allowed scope `{operation.allowed_scope}` for operation `{operation.operation_id}`."
        )
    expected_executor = SUPPORTED_EXECUTOR_KIND[operation.operation_kind]
    if operation.executor_kind != expected_executor:
        raise ValueError(
            f"Unsupported executor kind `{operation.executor_kind}` for operation `{operation.operation_id}`; "
            f"expected `{expected_executor}`."
        )
    if approval_mode == "review_only":
        raise ValueError("OfficeX patch bundles in `review_only` mode are non-executable.")
    if operation.risk_level in {"high", "prohibited"}:
        raise ValueError(
            f"OfficeX operation `{operation.operation_id}` is `{operation.risk_level}` risk and is non-executable in the MVP patch bridge."
        )
    if operation.requires_user_confirmation:
        raise ValueError(
            f"OfficeX operation `{operation.operation_id}` requires explicit user confirmation and cannot be batch-executed."
        )
    if anchor.candidate_hash != current_candidate_hash:
        raise ValueError(f"Anchor `{anchor.anchor_id}` no longer matches the current candidate hash.")


def _build_execution_operation(
    operation: OfficeXPatchOperation,
    anchor: OfficeXLiveAnchorRecord,
) -> OfficeXExecutionOperation:
    action = SUPPORTED_OPERATION_KIND_TO_ACTION[operation.operation_kind]
    if operation.operation_kind == "replace_text":
        text = str(operation.proposed_change.get("text", "")).strip()
        if not text:
            raise ValueError(f"OfficeX operation `{operation.operation_id}` is missing replacement `text`.")
        postconditions = [OfficeXExecutionPostcondition(kind="paragraph_text_equals", value=text)]
        payload = {"text": text}
    elif operation.operation_kind == "insert_paragraph":
        text = str(operation.proposed_change.get("text", "")).strip()
        if not text:
            raise ValueError(f"OfficeX operation `{operation.operation_id}` is missing insert `text`.")
        style = operation.proposed_change.get("style")
        postconditions = [OfficeXExecutionPostcondition(kind="inserted_paragraph_after_anchor", value=text, style=style)]
        payload = {"text": text, "style": style}
    else:
        style = str(operation.proposed_change.get("style", "")).strip()
        if not style:
            raise ValueError(f"OfficeX operation `{operation.operation_id}` is missing paragraph `style`.")
        postconditions = [OfficeXExecutionPostcondition(kind="paragraph_style_equals", style=style)]
        payload = {"style": style}

    return OfficeXExecutionOperation(
        operation_id=operation.operation_id,
        issue_id=anchor.issue_id,
        anchor_id=anchor.anchor_id,
        expected_candidate_hash=anchor.candidate_hash,
        action=action,
        payload=payload,
        evidence_refs=[],
        postconditions=postconditions,
    )


def render_officex_patch_spec_markdown(spec: OfficeXExecutionPatchSpec) -> str:
    lines = [
        "# OfficeX Patch Spec",
        "",
        f"- Spec id: `{spec.spec_id}`",
        f"- Generated at (UTC): `{spec.generated_at_utc}`",
        f"- Candidate path: `{spec.candidate_path}`",
        f"- Candidate hash: `{spec.candidate_hash}`",
        f"- Anchor snapshot: `{spec.anchor_snapshot_path}`",
        f"- Target issue ids: {', '.join(spec.target_issue_ids)}",
        f"- Operation count: {len(spec.operations)}",
        "",
        "## Anchors",
        "",
    ]
    for anchor in spec.anchor_records:
        lines.extend(
            [
                f"- `{anchor.anchor_id}`",
                f"  issue `{anchor.issue_id}` / role `{anchor.anchor_role}` / location `{anchor.location_hint}`",
                f"  excerpt: {anchor.text_excerpt or '[none]'}",
            ]
        )

    lines.extend(["", "## Operations", ""])
    for operation in spec.operations:
        payload_summary = ", ".join(
            f"{key}={value!r}" for key, value in operation.payload.items() if value
        )
        lines.extend(
            [
                f"- `{operation.operation_id}`",
                f"  issue `{operation.issue_id}` / action `{operation.action}` / anchor `{operation.anchor_id}`",
                f"  payload: {payload_summary or '[none]'}",
            ]
        )
    return "\n".join(lines)


def build_patch_spec_from_officex_bundle(
    *,
    patch_bundle_path: Path,
    candidate_path: Path,
    anchor_snapshot_path: Path,
) -> tuple[OfficeXPatchBundle, OfficeXLiveAnchorSnapshot, OfficeXExecutionPatchSpec]:
    resolved_bundle_path = patch_bundle_path.expanduser().resolve()
    resolved_candidate_path = candidate_path.expanduser().resolve()
    resolved_snapshot_path = anchor_snapshot_path.expanduser().resolve()

    patch_bundle = load_officex_patch_bundle(resolved_bundle_path)
    anchor_snapshot = load_live_anchor_snapshot(resolved_snapshot_path)

    resolved_candidate_path = ensure_mutable_candidate(resolved_candidate_path, action="mutate")
    if resolved_candidate_path != anchor_snapshot.candidate_path:
        raise ValueError(
            f"Refusing to apply OfficeX patch bundle for `{anchor_snapshot.candidate_path}` "
            f"to different candidate `{resolved_candidate_path}`."
        )

    candidate_hash = compute_file_sha256(resolved_candidate_path)
    if candidate_hash != anchor_snapshot.candidate_hash:
        raise ValueError(
            f"Candidate hash mismatch for `{resolved_candidate_path}`: "
            f"expected `{anchor_snapshot.candidate_hash}`, got `{candidate_hash}`."
        )

    anchor_map = {anchor.anchor_id: anchor for anchor in anchor_snapshot.anchors}
    used_anchors: list[OfficeXLiveAnchorRecord] = []
    seen_anchor_ids: set[str] = set()
    operations: list[OfficeXExecutionOperation] = []

    for operation in patch_bundle.operations:
        anchor = _resolve_anchor(anchor_map, operation)
        _validate_operation(
            operation,
            anchor,
            approval_mode=patch_bundle.approval_mode,
            current_candidate_hash=candidate_hash,
        )
        operations.append(_build_execution_operation(operation, anchor))
        if anchor.anchor_id not in seen_anchor_ids:
            seen_anchor_ids.add(anchor.anchor_id)
            used_anchors.append(anchor)

    spec = OfficeXExecutionPatchSpec(
        spec_id=patch_bundle.patch_bundle_id,
        generated_at_utc=utc_now_iso(),
        candidate_path=resolved_candidate_path,
        candidate_hash=candidate_hash,
        anchor_snapshot_path=resolved_snapshot_path,
        target_issue_ids=sorted({anchor.issue_id for anchor in used_anchors}),
        anchor_records=used_anchors,
        operations=operations,
    )
    return patch_bundle, anchor_snapshot, spec


def apply_officex_patch_bundle(
    *,
    patch_bundle_path: Path,
    candidate_path: Path,
    anchor_snapshot_path: Path,
    dry_run: bool,
) -> OfficeXPatchBridgeReport:
    patch_bundle, _snapshot, spec = build_patch_spec_from_officex_bundle(
        patch_bundle_path=patch_bundle_path,
        candidate_path=candidate_path,
        anchor_snapshot_path=anchor_snapshot_path,
    )
    artifact_dir = resolve_runtime_artifact_dir(
        spec.candidate_path,
        runtime_subdir="patch_bridge_runs",
        artifact_id=patch_bundle.patch_bundle_id,
        hidden_dir_name=".officex_patch_bridge",
    )
    spec_path = artifact_dir / "officex_patch_spec.yml"
    spec_markdown_path = artifact_dir / "officex_patch_spec.md"
    execution_report_path = artifact_dir / (
        "officex_execution_report_dry_run.json" if dry_run else "officex_execution_report.json"
    )
    execution_markdown_path = artifact_dir / (
        "officex_execution_report_dry_run.md" if dry_run else "officex_execution_report.md"
    )

    write_runtime_yaml(spec_path, spec.model_dump(mode="json"))
    write_runtime_markdown(spec_markdown_path, render_officex_patch_spec_markdown(spec))

    execution_report: OfficeXExecutionReport = execute_officex_patch_spec(
        spec.candidate_path,
        spec_path,
        dry_run=dry_run,
        backup_dir=artifact_dir / "backups",
    )
    write_runtime_json(execution_report_path, execution_report.model_dump(mode="json"))
    write_runtime_markdown(
        execution_markdown_path, render_officex_execution_markdown(execution_report)
    )

    return OfficeXPatchBridgeReport(
        bridge_run_id=make_exec_id("officex-patch-bridge"),
        patch_bundle_id=patch_bundle.patch_bundle_id,
        target_document_id=patch_bundle.target_document_id,
        candidate_path=spec.candidate_path,
        anchor_snapshot_path=spec.anchor_snapshot_path,
        patch_spec_path=spec_path,
        execution_report_path=execution_report_path,
        dry_run=dry_run,
        status=execution_report.status,
        operation_count=len(spec.operations),
        applied_operation_count=len(execution_report.applied_operations),
        rejected_operation_count=len(execution_report.rejected_operations),
        output_candidate_hash=execution_report.output_candidate_hash,
        backup_path=execution_report.backup_path,
        failure_reason=execution_report.failure_reason,
    )
