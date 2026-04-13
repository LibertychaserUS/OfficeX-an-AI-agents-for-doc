from __future__ import annotations

from pathlib import Path
from typing import Optional

from .common import load_json_model, load_yaml_model, make_run_id, render_context_lines, utc_now_iso
from .issue_profiles import build_issue_operations, planned_status_recommendations, resolve_target_issue_ids
from .models import LiveAnchorRecord, LiveAnchorSnapshot, RevisionIssueLedger, RevisionPatchSpec


def _anchor_map(snapshot: LiveAnchorSnapshot, issue_id: str) -> dict[str, LiveAnchorRecord]:
    mapping = {
        anchor.anchor_role or anchor.anchor_id: anchor
        for anchor in snapshot.anchors
        if anchor.issue_id == issue_id
    }
    expected = [anchor for anchor in snapshot.anchors if anchor.issue_id == issue_id]
    for anchor in expected:
        if anchor.uniqueness_status != "unique":
            raise ValueError(
                f"Cannot build patch for {issue_id}: anchor `{anchor.anchor_role}` is `{anchor.uniqueness_status}`."
            )
    return mapping


def build_revision_patch_spec(
    issue_ledger_path: Path,
    anchor_snapshot_path: Path,
    issue_ids: Optional[list[str]] = None,
) -> RevisionPatchSpec:
    ledger = load_yaml_model(issue_ledger_path.expanduser().resolve(), RevisionIssueLedger)
    snapshot = load_json_model(anchor_snapshot_path.expanduser().resolve(), LiveAnchorSnapshot)
    target_issue_ids = issue_ids or snapshot.target_issue_ids or resolve_target_issue_ids(ledger)

    operations = []
    anchor_records: list[LiveAnchorRecord] = []
    seen_anchor_ids: set[str] = set()

    for issue_id in target_issue_ids:
        issue_anchor_map = _anchor_map(snapshot, issue_id)
        operations.extend(build_issue_operations(issue_id, issue_anchor_map, ledger))
        for anchor in issue_anchor_map.values():
            if anchor.anchor_id in seen_anchor_ids:
                continue
            seen_anchor_ids.add(anchor.anchor_id)
            anchor_records.append(anchor)

    return RevisionPatchSpec(
        patch_id=make_run_id("revision-patch"),
        generated_at_utc=utc_now_iso(),
        issue_ledger_path=issue_ledger_path.expanduser().resolve(),
        candidate_path=snapshot.candidate_path,
        candidate_hash=snapshot.candidate_hash,
        anchor_snapshot_path=anchor_snapshot_path.expanduser().resolve(),
        target_issue_ids=target_issue_ids,
        anchor_records=anchor_records,
        operations=operations,
        status_recommendations=planned_status_recommendations(target_issue_ids),
    )


def render_revision_patch_markdown(spec: RevisionPatchSpec) -> str:
    lines = [
        "# Revision Patch Spec",
        "",
        f"- Patch id: `{spec.patch_id}`",
        f"- Generated at (UTC): `{spec.generated_at_utc}`",
        f"- Candidate path: `{spec.candidate_path}`",
        f"- Candidate hash: `{spec.candidate_hash}`",
        f"- Anchor snapshot: `{spec.anchor_snapshot_path}`",
        f"- Issue ledger: `{spec.issue_ledger_path}`",
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
                f"  leading: {render_context_lines(anchor.leading_context)}",
                f"  trailing: {render_context_lines(anchor.trailing_context)}",
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
                f"  postconditions: {', '.join(condition.kind for condition in operation.postconditions)}",
            ]
        )

    lines.extend(["", "## Status Recommendations", ""])
    for recommendation in spec.status_recommendations:
        lines.append(
            f"- `{recommendation.issue_id}` -> `{recommendation.recommended_status}`: {recommendation.rationale}"
        )
    return "\n".join(lines)
