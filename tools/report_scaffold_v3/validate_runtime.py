"""OfficeX validate: structural and semantic checks for any existing docx.

Runs two of the three verification tracks without an API key or a renderer:

1. Structural: page geometry, style contract, image fit and direct-formatting
   overrides against a document profile (same validator `officex generate` uses).
2. Semantic: citations vs bibliography, figure/table numbering, appendix and
   section cross-references, figure placement, terminology consistency.

The visual track needs LibreOffice and is run separately by
`officex audit visual`.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from docx import Document

from .manifest_loader import load_layout_contract, load_template_profile
from .models import LayoutContractManifest, TemplateProfileManifest
from .profile_runtime import PROFILES_DIR, get_active_profile_id
from .semantic_validation import run_semantic_validation

NOT_CHECKED = (
    "Rendered layout (blank pages, large white gaps, figure aspect ratio) is not checked here; "
    "run `officex audit visual`."
)


def _load_profile_contracts(profile_id: str | None) -> tuple[str | None, dict, dict]:
    """Return (profile_id, template_profile, layout_contract) without activating anything."""
    if profile_id is None:
        return (
            get_active_profile_id(),
            load_template_profile().model_dump(mode="json"),
            load_layout_contract().model_dump(mode="json"),
        )

    profile_dir = PROFILES_DIR / profile_id
    if not profile_dir.is_dir():
        available = sorted(p.name for p in PROFILES_DIR.iterdir() if p.is_dir())
        raise ValueError(f"Profile `{profile_id}` not found. Available: {', '.join(available) or 'none'}")

    def load(name: str, model_type):
        raw = yaml.safe_load((profile_dir / name).read_text(encoding="utf-8")) or {}
        return model_type.model_validate(raw).model_dump(mode="json")

    return (
        profile_id,
        load("template_profile.yml", TemplateProfileManifest),
        load("layout_contract.yml", LayoutContractManifest),
    )


def extract_paragraphs(docx_path: Path) -> list[dict]:
    """Body paragraphs in document order, in the shape semantic validation expects."""
    document = Document(str(docx_path))
    return [
        {
            "index": index,
            "style": paragraph.style.name if paragraph.style is not None else "",
            "text": paragraph.text,
        }
        for index, paragraph in enumerate(document.paragraphs)
    ]


def _count(findings: list[dict], severity: str) -> int:
    return sum(1 for finding in findings if finding["severity"] == severity)


def run_validate(
    docx_path: Path,
    *,
    profile_id: str | None = None,
    output_dir: Path | None = None,
) -> dict:
    """Validate a docx structurally and semantically; optionally write reports to output_dir."""
    from .docx_inspector import inspect_docx, inspect_docx_overrides
    from .ooxml_inspector import extract_effective_style_inventory
    from .validation import build_validation_report, render_validation_markdown

    docx_path = docx_path.expanduser().resolve()
    resolved_profile, template_profile, layout_contract = _load_profile_contracts(profile_id)

    structural_report = build_validation_report(
        docx_path,
        inspect_docx(docx_path),
        target_role="candidate_output",
        template_profile=template_profile,
        layout_contract=layout_contract,
        style_inventory=extract_effective_style_inventory(docx_path),
        override_inventory=inspect_docx_overrides(docx_path),
    )
    structural_findings = [finding.model_dump(mode="json") for finding in structural_report.findings]
    semantic = run_semantic_validation(extract_paragraphs(docx_path), source_label=str(docx_path)).to_dict()

    error_count = _count(structural_findings, "error") + semantic["error_count"]
    warning_count = _count(structural_findings, "warning") + semantic["warning_count"]
    if error_count:
        status = "fail"
    elif warning_count:
        status = "warning"
    else:
        status = "pass"

    payload: dict = {
        "docx_path": str(docx_path),
        "profile": resolved_profile,
        "status": status,
        "error_count": error_count,
        "warning_count": warning_count,
        "structural": {
            "error_count": _count(structural_findings, "error"),
            "warning_count": _count(structural_findings, "warning"),
            "summary": structural_report.summary,
            "findings": structural_findings,
        },
        "semantic": semantic,
        "not_checked": NOT_CHECKED,
        "report_paths": {},
    }

    if output_dir is not None:
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "structural_json": output_dir / "structural_validation.json",
            "structural_markdown": output_dir / "structural_validation.md",
            "semantic_json": output_dir / "semantic_validation.json",
            "summary_json": output_dir / "validate_summary.json",
        }
        paths["structural_json"].write_text(
            json.dumps(structural_report.model_dump(mode="json"), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        paths["structural_markdown"].write_text(
            render_validation_markdown(structural_report).strip() + "\n", encoding="utf-8"
        )
        paths["semantic_json"].write_text(json.dumps(semantic, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["report_paths"] = {key: str(path) for key, path in paths.items()}
        paths["summary_json"].write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return payload
