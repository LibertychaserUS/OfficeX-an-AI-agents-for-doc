from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RevisionIssueRecord(BaseModel):
    issue_id: str
    criterion: Optional[str] = None
    title: Optional[str] = None
    priority: Optional[str] = None
    status: str
    type: Optional[str] = None
    action: Optional[str] = None
    report_area: Optional[str] = None
    assets_required: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


class RevisionIssueLedger(BaseModel):
    ledger_id: str
    source_review: Path
    source_map: Path
    reference_report_role: str
    reference_report_path: Path
    execution_target_role: str
    execution_target_path: Path
    issues: list[RevisionIssueRecord] = Field(default_factory=list)


class AnchorLocation(BaseModel):
    block_kind: Literal["paragraph", "heading", "table_cell"]
    paragraph_index: Optional[int] = None
    table_index: Optional[int] = None
    row_index: Optional[int] = None
    column_index: Optional[int] = None


class LiveAnchorRecord(BaseModel):
    candidate_path: Path
    candidate_hash: str
    issue_id: str
    anchor_id: str
    anchor_role: Optional[str] = None
    block_kind: Literal["paragraph", "heading", "table_cell"]
    location_hint: str
    location: AnchorLocation
    normalized_fingerprint: str
    uniqueness_status: Literal["unique", "missing", "non_unique"]
    text_excerpt: str
    style_name: Optional[str] = None
    leading_context: list[str] = Field(default_factory=list)
    trailing_context: list[str] = Field(default_factory=list)
    match_count: int = 1


class LiveAnchorSnapshot(BaseModel):
    schema_version: int = 1
    snapshot_id: str
    generated_at_utc: str
    candidate_path: Path
    candidate_hash: str
    issue_ledger_path: Path
    target_issue_ids: list[str] = Field(default_factory=list)
    anchors: list[LiveAnchorRecord] = Field(default_factory=list)


class RevisionPostcondition(BaseModel):
    kind: Literal[
        "paragraph_text_equals",
        "paragraph_text_startswith",
        "paragraph_style_equals",
        "inserted_paragraph_after_anchor",
        "table_cell_text_equals",
    ]
    value: Optional[str] = None
    style: Optional[str] = None


class RevisionOperation(BaseModel):
    operation_id: str
    issue_id: str
    anchor_id: str
    expected_candidate_hash: str
    action: Literal[
        "insert_paragraph_after",
        "replace_paragraph_text",
        "update_paragraph_style",
        "split_heading_and_body",
        "update_table_cell",
    ]
    payload: dict = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    postconditions: list[RevisionPostcondition] = Field(default_factory=list)


class IssueStatusRecommendation(BaseModel):
    issue_id: str
    recommended_status: Literal["planned", "fixed", "verified"]
    rationale: str


class RevisionPatchSpec(BaseModel):
    schema_version: int = 1
    patch_id: str
    generated_at_utc: str
    issue_ledger_path: Path
    candidate_path: Path
    candidate_hash: str
    anchor_snapshot_path: Path
    target_issue_ids: list[str] = Field(default_factory=list)
    anchor_records: list[LiveAnchorRecord] = Field(default_factory=list)
    operations: list[RevisionOperation] = Field(default_factory=list)
    status_recommendations: list[IssueStatusRecommendation] = Field(default_factory=list)


class RevisionOperationExecutionResult(BaseModel):
    operation_id: str
    issue_id: str
    anchor_id: str
    action: str
    status: Literal["validated", "applied", "rejected"]
    target_summary: str
    postconditions_checked: int = 0
    reason: Optional[str] = None


class RevisionExecutionReport(BaseModel):
    schema_version: int = 1
    run_id: str
    patch_id: str
    input_candidate: Path
    input_candidate_hash: str
    backup_path: Optional[Path] = None
    patch_spec_path: Path
    dry_run: bool
    applied_operations: list[RevisionOperationExecutionResult] = Field(default_factory=list)
    rejected_operations: list[RevisionOperationExecutionResult] = Field(default_factory=list)
    output_candidate_hash: Optional[str] = None
    failure_reason: Optional[str] = None
    status: Literal["validated", "applied", "failed"]


class RevisionPostconditionResult(BaseModel):
    operation_id: str
    issue_id: str
    passed: bool
    messages: list[str] = Field(default_factory=list)


class OutlineRegressionSummary(BaseModel):
    has_regression: bool = False
    before_heading_count: int
    after_heading_count: int
    before_heading_level_counts: dict[str, int] = Field(default_factory=dict)
    after_heading_level_counts: dict[str, int] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)


class RevisionAuditReport(BaseModel):
    schema_version: int = 1
    run_id: str
    target_issue_ids: list[str] = Field(default_factory=list)
    input_candidate_hash: str
    output_candidate_hash: str
    protected_original_hash: str
    postcondition_results: list[RevisionPostconditionResult] = Field(default_factory=list)
    outline_regression: OutlineRegressionSummary
    non_target_drift_findings: list[str] = Field(default_factory=list)
    status: Literal["passed", "failed"]
    fixed_issue_ids: list[str] = Field(default_factory=list)
    remaining_issue_ids: list[str] = Field(default_factory=list)
    status_recommendations: list[IssueStatusRecommendation] = Field(default_factory=list)
