from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .runtime_common import local_now_iso


OfficeXCheckStatus = Literal["pass", "warning", "fail", "skipped"]
OfficeXDocumentLength = Literal["short", "medium", "long", "ultra_long"]
OfficeXScenarioStatus = Literal["pass", "warning", "fail", "not_supported"]


class OfficeXDoctorCheck(BaseModel):
    check_id: str
    title: str
    status: OfficeXCheckStatus
    summary: str
    detail_lines: list[str] = Field(default_factory=list)
    remediation: list[str] = Field(default_factory=list)


class OfficeXDoctorReport(BaseModel):
    report_id: str
    generated_at: str = Field(default_factory=local_now_iso)
    overall_status: OfficeXCheckStatus
    platform: str
    workspace_root: Path
    sandbox_root: Path
    machine_settings_dir: Path
    desktop_shell_dir: Path
    recommended_next_action: str
    report_json_path: Path | None = None
    report_markdown_path: Path | None = None
    checks: list[OfficeXDoctorCheck] = Field(default_factory=list)


class OfficeXRendererEnvironmentProfile(BaseModel):
    renderer_id: str
    display_name: str
    detected: bool
    app_path: Path | None = None
    version: str | None = None
    acceptance_role: Literal["primary", "mirror", "fallback"] = "primary"


class OfficeXRenderBoundaryScenario(BaseModel):
    scenario_id: str
    document_length: OfficeXDocumentLength
    structure_profile: str
    operation_profile: str
    status: OfficeXScenarioStatus
    localization_confidence: float
    patch_applicability_confidence: float
    requires_human_review: bool
    notes: list[str] = Field(default_factory=list)


class OfficeXRenderBoundaryReport(BaseModel):
    report_id: str
    generated_at: str = Field(default_factory=local_now_iso)
    overall_status: OfficeXCheckStatus
    workspace_root: Path
    sandbox_root: Path
    machine_settings_dir: Path | None = None
    renderer_profile: OfficeXRendererEnvironmentProfile
    capability_matrix: dict[str, dict[str, str]] = Field(default_factory=dict)
    residual_risk_notes: list[str] = Field(default_factory=list)
    source_fixture_dir: Path | None = None
    benchmark_run_root: Path | None = None
    report_json_path: Path | None = None
    report_markdown_path: Path | None = None
    scenarios: list[OfficeXRenderBoundaryScenario] = Field(default_factory=list)
