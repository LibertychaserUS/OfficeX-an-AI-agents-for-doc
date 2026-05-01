"""Validation subpackage.

Public API preserved from the original monolithic validation module:
  - build_validation_report
  - render_validation_markdown
  - build_page_setup_findings
  - build_style_contract_findings
  - build_image_fit_findings
  - build_direct_override_findings
  - style_has_expected_font
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

from ..docx_inspector import normalize_text
from ..models import ValidationFinding, ValidationReport

from .common import severity_for_role, summarize_ids
from .image_fit import build_image_fit_findings
from .override_detection import build_direct_override_findings
from .page_setup import build_page_setup_findings
from .style_contract import build_style_contract_findings, style_has_expected_font


def classify_figure_evidence_kind(figure: dict) -> str:
    caption_tail = normalize_text(figure.get("caption_tail", "")).lower()
    if caption_tail.startswith("wireframe"):
        return "wireframe"
    if caption_tail.startswith("screenshot"):
        return "screenshot"
    return "other"


def build_validation_report(
    docx_path: Path,
    inventory: dict,
    *,
    target_role: str = "reference_sample",
    format_authority_docx: Optional[Path] = None,
    template_profile: Optional[dict] = None,
    layout_contract: Optional[dict] = None,
    style_inventory: Optional[dict] = None,
    override_inventory: Optional[dict] = None,
    ooxml_context: Optional[dict] = None,
) -> ValidationReport:
    findings: list[ValidationFinding] = []
    summary = dict(inventory["summary"])
    summary["target_docx_role"] = target_role

    if target_role == "reference_sample":
        message = "This document is being treated as a reference sample, not the authoritative formatting baseline."
        if format_authority_docx is not None:
            message += f" Formatting authority: `{format_authority_docx}`."
        findings.append(
            ValidationFinding(
                severity="info",
                code="reference-sample-mode",
                message=message,
            )
        )

    if summary["heading_count"] == 0:
        findings.append(
            ValidationFinding(
                severity="error",
                code="missing-headings",
                message="No heading paragraphs were detected in the target docx.",
            )
        )

    grouped_figures: dict[tuple[str, str], list[dict]] = defaultdict(list)
    if style_inventory is None and ooxml_context is not None:
        style_inventory = ooxml_context
    for figure in inventory["figures"]:
        grouped_figures[(figure["figure_label"], figure["figure_id"])].append(figure)

    paired_evidence_ids: list[str] = []
    for (figure_label, figure_id), figures in grouped_figures.items():
        if len(figures) <= 1:
            continue

        evidence_kinds = Counter(classify_figure_evidence_kind(figure) for figure in figures)
        is_expected_pair = (
            figure_label in {"Figure", "Fig."}
            and len(figures) == 2
            and evidence_kinds["wireframe"] == 1
            and evidence_kinds["screenshot"] == 1
        )

        if is_expected_pair:
            paired_evidence_ids.append(figure_id)
            continue

        findings.append(
            ValidationFinding(
                severity=severity_for_role(target_role),
                code="duplicate-figure-id",
                message=f"{figure_label} id `{figure_id}` appears {len(figures)} times.",
            )
        )

    if paired_evidence_ids:
        findings.append(
            ValidationFinding(
                severity="info",
                code="paired-evidence-figure-id-reuse",
                message=(
                    f"{len(paired_evidence_ids)} figure ids are reused as matched wireframe/screenshot "
                    f"evidence pairs: {summarize_ids(paired_evidence_ids)}."
                ),
            )
        )

    missing_bindings = [
        figure for figure in inventory["figures"] if figure["image_paragraph_index"] is None
    ]
    for figure in missing_bindings:
        findings.append(
            ValidationFinding(
                severity=severity_for_role(target_role),
                code="caption-without-image-binding",
                message=(
                    f"Caption `{figure['caption_text']}` at paragraph "
                    f"{figure['caption_paragraph_index']} does not have a nearby image binding."
                ),
            )
        )

    for figure in inventory["figures"]:
        for relationship_id in figure["image_relationship_ids"]:
            if relationship_id not in inventory["image_relationships"]:
                findings.append(
                    ValidationFinding(
                        severity="error",
                        code="missing-image-relationship",
                        message=(
                            f"Figure `{figure['figure_id']}` references missing image relationship "
                            f"`{relationship_id}`."
                        ),
                    )
                )

    if summary["appendix_heading_count"] == 0:
        findings.append(
            ValidationFinding(
                severity=severity_for_role(target_role),
                code="appendix-not-detected",
                message="No appendix heading was detected in the current docx import.",
            )
        )

    findings.extend(
        build_page_setup_findings(
            inventory,
            template_profile,
            target_role=target_role,
        )
    )
    findings.extend(
        build_style_contract_findings(
            template_profile,
            style_inventory,
            target_role=target_role,
        )
    )
    findings.extend(
        build_image_fit_findings(
            inventory,
            layout_contract,
            target_role=target_role,
        )
    )
    findings.extend(
        build_direct_override_findings(
            inventory,
            template_profile,
            override_inventory,
            target_role=target_role,
        )
    )

    findings.append(
        ValidationFinding(
            severity="info",
            code="validation-scope",
            message=(
                "This validator currently checks structural bindings, sample-vs-authority context, "
                "template/style drift, page geometry, and image-fit risk. Semantic section-to-code "
                "alignment will be added in later scaffold stages."
            ),
        )
    )

    return ValidationReport(source_docx=docx_path, summary=summary, findings=findings)


def render_validation_markdown(report: ValidationReport) -> str:
    lines = [
        "# Validation Report",
        "",
        f"- Source docx: `{report.source_docx}`",
        f"- Target role: `{report.summary.get('target_docx_role', 'unspecified')}`",
        f"- Paragraphs: {report.summary['paragraph_count']}",
        f"- Headings: {report.summary['heading_count']}",
        f"- Figures: {report.summary['figure_count']}",
        f"- Image relationships: {report.summary['image_relationship_count']}",
        "",
        "## Findings",
        "",
    ]
    for finding in report.findings:
        lines.append(f"- [{finding.severity.upper()}] `{finding.code}`: {finding.message}")
    return "\n".join(lines)
