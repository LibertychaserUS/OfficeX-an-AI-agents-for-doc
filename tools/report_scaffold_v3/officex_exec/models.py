from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


class OfficeXAnchorLocation(BaseModel):
    block_kind: Literal["paragraph", "heading", "table_cell"]
    paragraph_index: Optional[int] = None
    table_index: Optional[int] = None
    row_index: Optional[int] = None
    column_index: Optional[int] = None


class OfficeXLiveAnchorRecord(BaseModel):
    candidate_path: Path
    candidate_hash: str
    issue_id: str
    anchor_id: str
    anchor_role: Optional[str] = None
    block_kind: Literal["paragraph", "heading", "table_cell"]
    location_hint: str
    location: OfficeXAnchorLocation
    normalized_fingerprint: str
    uniqueness_status: Literal["unique", "missing", "non_unique"]
    text_excerpt: str
    style_name: Optional[str] = None
    leading_context: list[str] = Field(default_factory=list)
    trailing_context: list[str] = Field(default_factory=list)
    match_count: int = 1


class OfficeXLiveAnchorSnapshot(BaseModel):
    schema_version: int = 1
    snapshot_id: str
    generated_at_utc: str
    candidate_path: Path
    candidate_hash: str
    source_review_ledger_path: Path
    target_issue_ids: list[str] = Field(default_factory=list)
    anchors: list[OfficeXLiveAnchorRecord] = Field(default_factory=list)


class OfficeXExecutionPostcondition(BaseModel):
    kind: Literal[
        "paragraph_text_equals",
        "paragraph_style_equals",
        "inserted_paragraph_after_anchor",
        "table_cell_text_equals",
    ]
    value: Optional[str] = None
    style: Optional[str] = None


class OfficeXExecutionOperation(BaseModel):
    operation_id: str
    issue_id: str
    anchor_id: str
    expected_candidate_hash: str
    action: Literal[
        "insert_paragraph_after",
        "replace_paragraph_text",
        "update_paragraph_style",
        "update_table_cell",
    ]
    payload: dict = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    postconditions: list[OfficeXExecutionPostcondition] = Field(default_factory=list)


class OfficeXExecutionPatchSpec(BaseModel):
    schema_version: int = 1
    spec_id: str
    generated_at_utc: str
    candidate_path: Path
    candidate_hash: str
    anchor_snapshot_path: Path
    target_issue_ids: list[str] = Field(default_factory=list)
    anchor_records: list[OfficeXLiveAnchorRecord] = Field(default_factory=list)
    operations: list[OfficeXExecutionOperation] = Field(default_factory=list)


class OfficeXOperationExecutionResult(BaseModel):
    operation_id: str
    issue_id: str
    anchor_id: str
    action: str
    status: Literal["validated", "applied", "rejected"]
    target_summary: str
    postconditions_checked: int = 0
    reason: Optional[str] = None


class OfficeXExecutionReport(BaseModel):
    schema_version: int = 1
    run_id: str
    spec_id: str
    input_candidate: Path
    input_candidate_hash: str
    spec_path: Path
    dry_run: bool
    applied_operations: list[OfficeXOperationExecutionResult] = Field(default_factory=list)
    rejected_operations: list[OfficeXOperationExecutionResult] = Field(default_factory=list)
    output_candidate_hash: Optional[str] = None
    backup_path: Optional[Path] = None
    failure_reason: Optional[str] = None
    status: Literal["validated", "applied", "failed"]
