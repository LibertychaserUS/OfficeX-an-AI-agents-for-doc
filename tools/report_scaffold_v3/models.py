from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class BaselineManifest(BaseModel):
    schema_version: int = 1
    workspace_root: Path
    scaffold_root: Path
    target_docx: Path
    target_docx_role: Literal["reference_sample", "template_authority", "candidate_output"] = (
        "reference_sample"
    )
    format_authority_docx: Optional[Path] = None
    read_only_reference_roots: list[Path] = Field(default_factory=list)


class ManagedSectionManifest(BaseModel):
    section_id: str
    title: str
    title_role: str
    paragraph_role: str
    source_path: Path
    include_title: bool = True
    split_mode: Literal["blank_lines"] = "blank_lines"


class SectionsManifest(BaseModel):
    schema_version: int = 1
    document_id: str = "section-assembled-demo"
    output_name: str = "section_assembled_demo.docx"
    managed_sections: list[ManagedSectionManifest] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ManagedFigureManifest(BaseModel):
    figure_id: str
    role: str = "figure"
    caption: str
    image_path: Path
    target_section_id: str
    placement: Literal["after_section"] = "after_section"
    order: int = 0


class FiguresManifest(BaseModel):
    schema_version: int = 1
    managed_figures: list[ManagedFigureManifest] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ManagedSnippetManifest(BaseModel):
    snippet_id: str
    title: str
    language: str = "text"
    source_path: Path
    target_section_id: str
    placement: Literal["after_section"] = "after_section"
    order: int = 0
    extract_mode: Literal["line_range", "literal_text"] = "line_range"
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    literal_text: Optional[str] = None
    label_role: str = "subtitle"
    code_role: str = "body"


class SnippetsManifest(BaseModel):
    schema_version: int = 1
    managed_snippets: list[ManagedSnippetManifest] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ManagedCitationManifest(BaseModel):
    citation_id: str
    reference_text: str
    section_tokens: list[str] = Field(default_factory=list)


class CitationsManifest(BaseModel):
    schema_version: int = 1
    managed_citations: list[ManagedCitationManifest] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class NavigationCatalogEntity(BaseModel):
    entity_id: str
    kind: str
    path: Path
    status: Literal["active", "active_reference", "read_only_reference", "legacy", "deprecated"]
    purpose: str
    source_of_truth: list[Path] = Field(default_factory=list)
    entrypoints: list[Path] = Field(default_factory=list)
    navigation_hints: list[str] = Field(default_factory=list)


class NavigationCatalogManifest(BaseModel):
    schema_version: int = 1
    catalog_id: str
    entities: list[NavigationCatalogEntity] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ProviderModelCapabilityManifest(BaseModel):
    model_id: str
    supports_structured_output: bool = False
    supports_tool_calls: bool = False
    supports_image_generation: bool = False
    supports_long_context: bool = False
    latency_class: Literal["low", "medium", "high"] = "medium"
    risk_notes: list[str] = Field(default_factory=list)


class ProviderCatalogEntryManifest(BaseModel):
    provider_id: str
    display_name: str
    adapter_kind: str
    status: Literal["active", "experimental", "planned"] = "active"
    auth_scheme: Literal["api_key", "local_none", "custom"] = "api_key"
    default_model_id: str
    config_fields: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    models: list[ProviderModelCapabilityManifest] = Field(default_factory=list)


class ProviderCatalogManifest(BaseModel):
    schema_version: int = 1
    catalog_id: str
    providers: list[ProviderCatalogEntryManifest] = Field(default_factory=list)


class AgentCatalogEntryManifest(BaseModel):
    agent_id: str
    display_name: str
    runtime_role: str
    status: Literal["active", "planned", "experimental"] = "active"
    prompt_roles: list[str] = Field(default_factory=list)
    domain_pack_candidates: list[str] = Field(default_factory=list)
    review_pack_candidates: list[str] = Field(default_factory=list)
    owned_capabilities: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AgentCatalogManifest(BaseModel):
    schema_version: int = 1
    catalog_id: str
    agents: list[AgentCatalogEntryManifest] = Field(default_factory=list)


class TemplateProfileManifest(BaseModel):
    schema_version: int = 1
    template_id: str
    source_template_docx: Path
    page_setup: dict = Field(default_factory=dict)
    document_defaults: dict = Field(default_factory=dict)
    style_contract: dict[str, dict] = Field(default_factory=dict)
    resolution_rules: list[str] = Field(default_factory=list)


class LayoutContractManifest(BaseModel):
    schema_version: int = 1
    template_id: str
    paragraph_position_rules: dict = Field(default_factory=dict)
    image_layout_rules: dict = Field(default_factory=dict)
    run_override_rules: dict = Field(default_factory=dict)
    cover_page_rules: dict = Field(default_factory=dict)


class WriteRoleManifest(BaseModel):
    style: str
    paragraph_format: dict = Field(default_factory=dict)
    run_format: dict = Field(default_factory=dict)
    allow_mixed_runs: bool = True


class ImageRoleManifest(BaseModel):
    caption_role: str
    width_mode: Literal["fit_usable_body_width", "fixed_width_pt"] = "fit_usable_body_width"
    max_width_pt: Optional[float] = None
    fixed_width_pt: Optional[float] = None
    center_paragraph: bool = True


class WriteContractManifest(BaseModel):
    schema_version: int = 1
    template_id: str
    default_output_strategy: dict = Field(default_factory=dict)
    paragraph_roles: dict[str, WriteRoleManifest] = Field(default_factory=dict)
    image_roles: dict[str, ImageRoleManifest] = Field(default_factory=dict)
    guardrails: dict = Field(default_factory=dict)


class ParagraphBlockSpec(BaseModel):
    kind: Literal["paragraph"] = "paragraph"
    role: str
    text: str


class ImageBlockSpec(BaseModel):
    kind: Literal["image"] = "image"
    role: str
    image_path: Path
    caption: str


class BuildSourceManifest(BaseModel):
    schema_version: int = 1
    document_id: str
    output_name: str
    blocks: list[dict] = Field(default_factory=list)


class BuildResult(BaseModel):
    document_id: str
    template_docx: Path
    output_docx: Path
    block_count: int
    paragraph_count: int
    image_count: int


class FontViolationExample(BaseModel):
    location: str
    snippet: str


class FontViolationGroup(BaseModel):
    font_name: str
    occurrences: int
    examples: list[FontViolationExample] = Field(default_factory=list)


class FontAuditReport(BaseModel):
    source_docx: Path
    expected_font: str
    total_runs_scanned: int
    explicit_expected_font_runs: int
    inherited_font_runs: int
    explicit_other_font_runs: int
    violations: list[FontViolationGroup] = Field(default_factory=list)


class OutlineHeadingRecord(BaseModel):
    paragraph_index: int
    level: int
    style_name: str
    text: str


class OutlineAuditReport(BaseModel):
    source_docx: Path
    heading_count: int
    appendix_heading_count: int
    heading_level_counts: dict[str, int] = Field(default_factory=dict)
    duplicate_heading_texts: list[str] = Field(default_factory=list)
    headings: list[OutlineHeadingRecord] = Field(default_factory=list)


class CandidateAuditFinding(BaseModel):
    severity: Literal["info", "warning", "error"]
    code: str
    message: str


class CandidateAuditReport(BaseModel):
    source_docx: Path
    expected_paragraph_count: Optional[int] = None
    actual_paragraph_count: int
    expected_heading_count: Optional[int] = None
    actual_heading_count: int
    expected_image_count: Optional[int] = None
    actual_figure_count: int = 0
    expected_snippet_count: Optional[int] = None
    actual_snippet_count: int = 0
    allowed_styles: list[str] = Field(default_factory=list)
    findings: list[CandidateAuditFinding] = Field(default_factory=list)


class SectionPipelineReport(BaseModel):
    build_source_path: Path
    output_docx: Path
    candidate_audit_path: Path
    validation_report_path: Path
    candidate_error_count: int
    candidate_warning_count: int
    validation_error_count: int
    validation_warning_count: int


ApprovalMode = Literal[
    "review_only",
    "ask_every_conflict",
    "scoped_auto_low_medium",
    "full_auto_in_sandbox",
]

ProviderDispatchMode = Literal["dry_run"]
ProviderResponseContractKind = Literal[
    "plan_object",
    "section_draft",
    "review_findings",
    "patch_bundle_draft",
]
OfficeXPatchIntent = Literal[
    "content_revision",
    "style_alignment",
    "layout_repair",
    "asset_insertion",
    "metadata_update",
    "mixed",
]
OfficeXPatchRiskLevel = Literal["low", "medium", "high", "prohibited"]


class OfficeXTaskPacket(BaseModel):
    task_packet_id: str
    goal: str
    task_family: str
    active_workspace: Path
    allowed_surfaces: list[str] = Field(default_factory=list)
    blocked_surfaces: list[str] = Field(default_factory=list)
    input_artifacts: list[Path] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    approval_mode: ApprovalMode = "ask_every_conflict"
    acceptance_gates: list[str] = Field(default_factory=list)
    publish_gate: str = "never_publish"
    expected_outputs: list[str] = Field(default_factory=list)


class OfficeXSandboxManifest(BaseModel):
    run_id: str
    sandbox_root: Path
    runtime_dir: Path
    input_dir: Path
    candidate_dir: Path
    reports_dir: Path
    source_reference_docx: Path
    mutable_template_docx: Path
    created_at: str


class OfficeXWorkspaceManifest(BaseModel):
    workspace_id: str
    root_path: Path
    runtime_dir: Path
    imports_dir: Path
    reports_dir: Path
    sandboxes_dir: Path
    exports_dir: Path
    active_profile: str
    active_page_profile: str
    status: Literal["active", "paused", "archived"] = "active"
    created_at: str


class OfficeXStageReview(BaseModel):
    stage_id: str
    status: Literal["completed", "warning", "blocked"] = "completed"
    history_check: str
    outputs: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class OfficeXDocxMvpRunReport(BaseModel):
    run_id: str
    sandbox_root: Path
    task_packet_path: Path
    sandbox_manifest_path: Path
    build_source_path: Path
    candidate_docx: Path
    validation_report_path: Path
    candidate_audit_path: Path
    stage_history_review_path: Path
    candidate_error_count: int
    candidate_warning_count: int
    validation_error_count: int
    validation_warning_count: int


class OfficeXPromptManifestEntry(BaseModel):
    layer: Literal["cognition", "role"]
    prompt_id: str
    ref: str


class OfficeXResolvedPromptRef(BaseModel):
    layer: Literal["cognition", "role"]
    prompt_id: str
    ref: str
    source_path: Path
    section_title: str
    content_sha256: str


class OfficeXPromptTraceRecord(BaseModel):
    role: str
    include_cognition: bool = True
    prompt_source_refs: list[str] = Field(default_factory=list)
    compiled_prompt_sha256: str


class OfficeXCompiledPromptBundle(BaseModel):
    role: str
    include_cognition: bool = True
    prompt_manifest: list[OfficeXPromptManifestEntry] = Field(default_factory=list)
    resolved_rule_refs: list[OfficeXResolvedPromptRef] = Field(default_factory=list)
    compiled_prompt_debug: str
    prompt_trace_record: OfficeXPromptTraceRecord


class OfficeXProviderPromptBinding(BaseModel):
    provider_id: str
    provider_display_name: str
    adapter_kind: str
    status: Literal["active", "experimental", "planned"] = "active"
    auth_scheme: Literal["api_key", "local_none", "custom"] = "api_key"
    model_id: str
    role: str
    include_cognition: bool = True
    supports_structured_output: bool = False
    supports_tool_calls: bool = False
    supports_image_generation: bool = False
    supports_long_context: bool = False
    latency_class: Literal["low", "medium", "high"] = "medium"
    config_fields: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    prompt_manifest: list[OfficeXPromptManifestEntry] = Field(default_factory=list)
    resolved_rule_refs: list[OfficeXResolvedPromptRef] = Field(default_factory=list)
    compiled_prompt_debug: str
    prompt_trace_record: OfficeXPromptTraceRecord
    prompt: str


class OfficeXProviderRequestEnvelope(BaseModel):
    envelope_id: str
    provider_id: str
    model_id: str
    adapter_kind: str
    dispatch_mode: ProviderDispatchMode = "dry_run"
    role: str
    include_cognition: bool = True
    task_packet_id: str
    goal: str
    task_family: str
    approval_mode: ApprovalMode = "ask_every_conflict"
    system_prompt: str
    prompt_manifest: list[OfficeXPromptManifestEntry] = Field(default_factory=list)
    resolved_rule_refs: list[OfficeXResolvedPromptRef] = Field(default_factory=list)
    compiled_prompt_debug: str
    prompt_trace_record: OfficeXPromptTraceRecord
    input_artifacts: list[Path] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    required_config_fields: list[str] = Field(default_factory=list)
    provided_config_fields: list[str] = Field(default_factory=list)
    response_contract_kind: ProviderResponseContractKind = "plan_object"
    supports_structured_output: bool = False
    supports_tool_calls: bool = False
    supports_image_generation: bool = False
    supports_long_context: bool = False
    latency_class: Literal["low", "medium", "high"] = "medium"


class OfficeXParagraphAnchorRule(BaseModel):
    anchor_rule_type: Literal["paragraph_text"] = "paragraph_text"
    anchor_role: str
    block_kind: Literal["paragraph", "heading"]
    match_mode: Literal["exact", "prefix"]
    needle: str


class OfficeXTableCellAnchorRule(BaseModel):
    anchor_rule_type: Literal["table_cell"] = "table_cell"
    anchor_role: str
    header_values: list[str] = Field(default_factory=list)
    row_key: str
    row_key_column: int
    target_column: int


OfficeXAnchorRule = Annotated[
    Union[OfficeXParagraphAnchorRule, OfficeXTableCellAnchorRule],
    Field(discriminator="anchor_rule_type"),
]


class OfficeXManualReviewFinding(BaseModel):
    issue_id: str
    title: str
    issue_kind: str
    severity: str
    status: str
    review_comment: str
    anchor_rule: OfficeXAnchorRule


class OfficeXManualReviewInput(BaseModel):
    review_id: str
    target_document_id: str
    generated_by: str
    findings: list[OfficeXManualReviewFinding] = Field(default_factory=list)


class OfficeXReviewLedgerFinding(BaseModel):
    issue_id: str
    title: str
    issue_kind: str
    severity: str
    status: str
    review_comment: str
    anchor_rule: OfficeXAnchorRule


class OfficeXReviewLedger(BaseModel):
    schema_version: int = 1
    review_id: str
    target_document_id: str
    generated_by: str
    findings: list[OfficeXReviewLedgerFinding] = Field(default_factory=list)


class OfficeXAnchorPrepReport(BaseModel):
    review_id: str
    target_document_id: str
    candidate_path: Path
    review_ledger_path: Path
    output_dir: Path
    anchor_snapshot_path: Path
    anchor_snapshot_markdown_path: Path
    issue_count: int
    anchor_count: int
    finding_count: int = 0


class OfficeXPatchOperation(BaseModel):
    operation_id: str
    operation_kind: str
    target_anchor_id: str
    allowed_scope: str
    proposed_change: dict = Field(default_factory=dict)
    risk_level: OfficeXPatchRiskLevel = "low"
    requires_user_confirmation: bool = False
    executor_kind: str
    expected_effects: list[str] = Field(default_factory=list)


class OfficeXPatchBundle(BaseModel):
    schema_version: int = 1
    patch_bundle_id: str
    run_id: str
    target_document_id: str
    generated_by: str
    patch_intent: OfficeXPatchIntent = "content_revision"
    operations: list[OfficeXPatchOperation] = Field(default_factory=list)
    approval_mode: ApprovalMode = "ask_every_conflict"
    approval_requirements: list[str] = Field(default_factory=list)
    verification_requirements: list[str] = Field(default_factory=list)


class OfficeXPatchBridgeReport(BaseModel):
    bridge_run_id: str
    patch_bundle_id: str
    target_document_id: str
    candidate_path: Path
    anchor_snapshot_path: Path
    patch_spec_path: Path
    execution_report_path: Path
    dry_run: bool
    status: Literal["validated", "applied", "failed"]
    operation_count: int
    applied_operation_count: int = 0
    rejected_operation_count: int = 0
    output_candidate_hash: Optional[str] = None
    backup_path: Optional[Path] = None
    failure_reason: Optional[str] = None


class OfficeXTraceCheckpointReport(BaseModel):
    checkpoint_id: str
    checkpoint_path: Path
    trace_dir: Path
    title: str
    summary_lines: list[str] = Field(default_factory=list)
    verification_lines: list[str] = Field(default_factory=list)
    follow_up_lines: list[str] = Field(default_factory=list)


class SnippetAuditFinding(BaseModel):
    severity: Literal["info", "warning", "error"]
    code: str
    message: str


class SnippetAuditEntry(BaseModel):
    snippet_id: str
    source_path: Path
    target_section_id: str
    language: str
    line_span: Optional[str] = None
    extracted_line_count: int
    preview: str


class SnippetAuditReport(BaseModel):
    source_manifest: Path
    snippets_checked: int
    findings: list[SnippetAuditFinding] = Field(default_factory=list)
    entries: list[SnippetAuditEntry] = Field(default_factory=list)


class PublishedRunManifest(BaseModel):
    published_id: str
    published_at_utc: str
    run_dir: Path
    canonical_root: Path
    build_source_path: Path
    output_docx: Path
    candidate_audit_path: Path
    validation_report_path: Path
    candidate_error_count: int
    candidate_warning_count: int
    validation_error_count: int
    validation_warning_count: int
    target_docx_role: Literal["candidate_output"] = "candidate_output"


class CheckpointCatalogEntry(BaseModel):
    checkpoint_number: int
    checkpoint_id: str
    path: Path
    title: Optional[str] = None
    date: Optional[str] = None
    backfilled: bool = False


class TraceIndexReport(BaseModel):
    trace_dir: Path
    checkpoint_count: int
    latest_checkpoint_id: Optional[str] = None
    missing_numbers: list[int] = Field(default_factory=list)
    entries: list[CheckpointCatalogEntry] = Field(default_factory=list)


class ValidationFinding(BaseModel):
    severity: Literal["info", "warning", "error"]
    code: str
    message: str


class ValidationReport(BaseModel):
    source_docx: Path
    summary: dict
    findings: list[ValidationFinding] = Field(default_factory=list)
