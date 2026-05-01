"""Long document generation: plan → section-by-section AI → assemble → build.

This module implements the independent Agent platform mode for generating
documents that exceed single-call AI limits. It:

1. Reads an outline (sections, requirements, materials)
2. Plans section-by-section generation with token budgets
3. Calls AI for each section independently
4. Assembles all sections into a unified BuildSourceManifest
5. Builds the docx and runs dual-track verification

This is a platform-mode capability. When OfficeX runs as a skill for
external agents, the external agent handles its own orchestration.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .generate_runtime import (
    GenerateReport,
    _build_generate_system_prompt,
    _extract_json_from_response,
    JSON_REPAIR_PROMPT,
)
from .manifest_loader import (
    load_baseline_manifest,
    load_layout_contract,
    load_template_profile,
    load_write_contract,
)
from .models import BuildSourceManifest, WriteContractManifest
from .paths import DEFAULT_BASELINE_MANIFEST, DEFAULT_WRITE_CONTRACT_MANIFEST, SANDBOXES_DIR
from .runtime_common import make_local_runtime_identifier, sanitize_runtime_identifier
from .writer import build_word_candidate

logger = logging.getLogger(__name__)


@dataclass
class SectionPlan:
    """Plan for generating one section of a document."""
    section_id: str
    heading: str
    requirements: str = ""
    materials: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    max_tokens: int = 2000


@dataclass
class DocumentPlan:
    """Full plan for a long document."""
    title: str
    sections: list[SectionPlan]
    review_criteria: list[str] = field(default_factory=list)
    review_interval: int = 3  # review every N sections


def load_outline(outline_path: Path) -> DocumentPlan:
    """Load a document outline from YAML.

    Expected format:
    ```yaml
    title: "Document Title"
    sections:
      - section_id: intro
        heading: "Introduction"
        requirements: "Provide context and background..."
        materials:
          - materials/intro_notes.md
      - section_id: methodology
        heading: "Methodology"
        requirements: "Describe the approach..."
    review_criteria:
      - "All claims must be supported by evidence"
      - "Professional tone throughout"
    ```
    """
    import yaml

    data = yaml.safe_load(outline_path.read_text(encoding="utf-8"))

    sections = []
    for s in data.get("sections", []):
        materials = []
        for m in s.get("materials", []):
            mat_path = Path(m)
            if not mat_path.is_absolute():
                mat_path = outline_path.parent / mat_path
            if mat_path.exists():
                materials.append(mat_path.read_text(encoding="utf-8"))
            else:
                logger.debug("Material not found: %s", mat_path)
        sections.append(SectionPlan(
            section_id=s.get("section_id", f"section_{len(sections)}"),
            heading=s.get("heading", ""),
            requirements=s.get("requirements", ""),
            materials=materials,
            depends_on=s.get("depends_on", []),
            max_tokens=s.get("max_tokens", 2000),
        ))

    return DocumentPlan(
        title=data.get("title", "Untitled"),
        sections=sections,
        review_criteria=data.get("review_criteria", []),
        review_interval=data.get("review_interval", 3),
    )


def _generate_section(
    *,
    client,
    model: str,
    section: SectionPlan,
    document_title: str,
    system_prompt: str,
    review_criteria: list[str],
    prior_sections: list[dict] | None = None,
) -> dict:
    """Generate content for a single section via AI.

    Constitution Article 23: later sections see all prior content
    to maintain single-author coherence.
    """
    materials_text = ""
    if section.materials:
        materials_text = "\n\nReference materials:\n" + "\n---\n".join(section.materials)

    criteria_text = ""
    if review_criteria:
        criteria_text = "\n\nReview criteria:\n" + "\n".join(f"- {c}" for c in review_criteria)

    # Include prior sections as context (Article 23)
    prior_context = ""
    if prior_sections:
        prior_lines = []
        for ps in prior_sections:
            prior_lines.append(f"## {ps['heading']}")
            for p in ps["paragraphs"][:3]:  # limit to avoid token explosion
                prior_lines.append(p[:200])
        prior_context = (
            "\n\nPreviously written sections (maintain consistency with these):\n"
            + "\n".join(prior_lines)
        )

    user_prompt = (
        f"You are writing the section '{section.heading}' of the document "
        f"titled '{document_title}'.\n\n"
        f"Requirements for this section:\n{section.requirements}\n"
        f"{materials_text}{criteria_text}{prior_context}\n\n"
        "Return ONLY a JSON object:\n"
        '{"paragraphs": ["paragraph 1 text", "paragraph 2 text", ...]}\n'
        "Write substantive, professional content. No markdown fences."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=section.max_tokens,
    )

    text = response.choices[0].message.content or ""
    usage = {}
    if response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    # Parse the section response
    try:
        extracted = _extract_json_from_response(text)
        data = json.loads(extracted)
        # AI might return {paragraphs: [...]} or {title, sections: [{heading, paragraphs}]}
        paragraphs = data.get("paragraphs", [])
        if not paragraphs and "sections" in data:
            # Flatten nested section structure
            for sec in data["sections"]:
                paragraphs.extend(sec.get("paragraphs", []))
    except (json.JSONDecodeError, KeyError):
        # If parsing fails, treat entire response as one paragraph
        paragraphs = [text.strip()] if text.strip() else []

    return {
        "section_id": section.section_id,
        "heading": section.heading,
        "paragraphs": paragraphs,
        "raw_response": text,
        "usage": usage,
    }


def _run_interleaved_review(
    *,
    client,
    model: str,
    generated_content: list[dict],
    review_criteria: list[str],
    document_title: str,
) -> dict:
    """Review generated sections for coherence and consistency.

    Constitution Article 24: review is interleaved during generation,
    not deferred to the end.
    """
    content_summary = []
    for gc in generated_content:
        content_summary.append(f"## {gc['heading']}")
        for p in gc["paragraphs"][:3]:
            content_summary.append(p[:300])

    criteria_text = "\n".join(f"- {c}" for c in review_criteria)

    user_prompt = (
        f"Review the following sections of '{document_title}' for coherence:\n\n"
        + "\n".join(content_summary)
        + f"\n\nReview criteria:\n{criteria_text}\n\n"
        "Return a JSON object:\n"
        '{"issues": ["issue 1", "issue 2"], "terminology_drift": [], "overall_coherence": "good|fair|poor"}\n'
        "If no issues found, return empty lists. No markdown fences."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a document reviewer checking for coherence, terminology consistency, and argument flow."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        text = response.choices[0].message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        try:
            data = json.loads(_extract_json_from_response(text))
        except (json.JSONDecodeError, KeyError):
            data = {"issues": [], "raw_response": text}
        data["usage"] = usage
        return data
    except Exception as exc:
        return {"issues": [], "error": str(exc), "usage": {}}


def run_long_generate(
    *,
    outline_path: Path,
    provider_id: str = "compatible_local",
    model_id: str | None = None,
    run_id: str | None = None,
    output_dir: Path | None = None,
    baseline_manifest_path: Path = DEFAULT_BASELINE_MANIFEST,
    write_contract_path: Path = DEFAULT_WRITE_CONTRACT_MANIFEST,
    include_visual_audit: bool = True,
) -> GenerateReport:
    """Generate a long document section-by-section from an outline."""
    run_id = run_id or sanitize_runtime_identifier(
        make_local_runtime_identifier("longgen"),
        fallback="officex-long-generate",
    )
    output_dir = (output_dir or SANDBOXES_DIR / run_id).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load outline
    plan = load_outline(outline_path)
    logger.debug("Loaded outline: %s with %d sections", plan.title, len(plan.sections))

    # Save plan
    (output_dir / "plan.json").write_text(
        json.dumps({
            "title": plan.title,
            "section_count": len(plan.sections),
            "sections": [{"id": s.section_id, "heading": s.heading} for s in plan.sections],
            "review_criteria": plan.review_criteria,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Setup provider
    api_key = os.environ.get("OFFICEX_PROVIDER_API_KEY")
    if not api_key:
        return GenerateReport(
            run_id=run_id, status="ai_failed",
            error_message="No API key. Set OFFICEX_PROVIDER_API_KEY.",
        )

    base_url = os.environ.get("OFFICEX_PROVIDER_BASE_URL")
    from openai import OpenAI
    client_kwargs: dict = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)
    resolved_model = model_id or "qwen-plus"

    # Build system prompt
    write_contract = load_write_contract(write_contract_path)
    from .prompt_runtime import compile_officex_prompt_bundle
    prompt_bundle = compile_officex_prompt_bundle("orchestrator", include_cognition=True)
    system_prompt = _build_generate_system_prompt(
        prompt_bundle.compiled_prompt_debug, write_contract,
    )

    # Generate each section
    total_tokens: dict = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    all_blocks: list[dict] = []

    # Title block
    all_blocks.append({"kind": "paragraph", "role": "heading_1", "text": plan.title})

    sections_dir = output_dir / "sections"
    sections_dir.mkdir(exist_ok=True)

    generated_content: list[dict] = []  # accumulates all generated sections for context

    for i, section in enumerate(plan.sections):
        logger.debug("Generating section %d/%d: %s", i + 1, len(plan.sections), section.heading)

        try:
            result = _generate_section(
                client=client,
                model=resolved_model,
                section=section,
                document_title=plan.title,
                system_prompt=system_prompt,
                review_criteria=plan.review_criteria,
                prior_sections=generated_content,
            )
        except Exception as exc:
            logger.error("Section %s failed: %s", section.section_id, exc)
            return GenerateReport(
                run_id=run_id, status="ai_failed", ai_model=resolved_model,
                ai_tokens=total_tokens,
                error_message=f"Section {section.section_id} failed: {exc}",
            )

        # Accumulate tokens
        for key in total_tokens:
            total_tokens[key] += result["usage"].get(key, 0)

        # Track generated content for context in subsequent sections
        generated_content.append({
            "heading": section.heading,
            "paragraphs": result["paragraphs"],
        })

        # Save section result
        (sections_dir / f"{section.section_id}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8",
        )

        # Add to blocks
        all_blocks.append({"kind": "paragraph", "role": "heading_2", "text": section.heading})
        for para in result["paragraphs"]:
            if para.strip():
                all_blocks.append({"kind": "paragraph", "role": "body", "text": para})

        # Interleaved review (Constitution Article 24)
        if (
            plan.review_interval > 0
            and (i + 1) % plan.review_interval == 0
            and i + 1 < len(plan.sections)
        ):
            review_result = _run_interleaved_review(
                client=client,
                model=resolved_model,
                generated_content=generated_content,
                review_criteria=plan.review_criteria,
                document_title=plan.title,
            )
            for key in total_tokens:
                total_tokens[key] += review_result.get("usage", {}).get(key, 0)

            (sections_dir / f"review_after_{section.section_id}.json").write_text(
                json.dumps(review_result, ensure_ascii=False, indent=2), encoding="utf-8",
            )

    # Assemble BuildSourceManifest
    output_name = f"{run_id}.docx"
    build_source = BuildSourceManifest(
        document_id=f"officex-{run_id}",
        output_name=output_name,
        blocks=all_blocks,
    )

    (output_dir / "build_source.json").write_text(
        json.dumps(build_source.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Build docx
    output_docx = output_dir / output_name
    try:
        baseline = load_baseline_manifest(baseline_manifest_path)
        template_docx = (
            baseline.format_authority_docx.expanduser().resolve()
            if baseline.format_authority_docx
            else baseline.target_docx.expanduser().resolve()
        )
        build_result = build_word_candidate(
            template_docx=template_docx,
            source=build_source,
            contract=write_contract,
            output_docx=output_docx,
        )
    except Exception as exc:
        return GenerateReport(
            run_id=run_id, status="build_failed", ai_model=resolved_model,
            ai_tokens=total_tokens, error_message=str(exc),
        )

    # Structural validation
    from .docx_inspector import inspect_docx, inspect_docx_overrides
    from .ooxml_inspector import extract_effective_style_inventory
    from .validation import build_validation_report

    template_profile = load_template_profile().model_dump(mode="json")
    layout_contract = load_layout_contract().model_dump(mode="json")
    inventory = inspect_docx(output_docx)
    val_report = build_validation_report(
        output_docx, inventory,
        target_role="candidate_output",
        template_profile=template_profile,
        layout_contract=layout_contract,
        style_inventory=extract_effective_style_inventory(output_docx),
        override_inventory=inspect_docx_overrides(output_docx),
    )
    val_errors = sum(1 for f in val_report.findings if f.severity == "error")
    val_warnings = sum(1 for f in val_report.findings if f.severity == "warning")

    (output_dir / "validation.json").write_text(
        json.dumps(val_report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Visual audit
    page_count = 0
    png_paths: list[Path] = []
    visual_finding_count = 0

    if include_visual_audit:
        from .visual_audit import render_docx_to_png
        from .visual_audit_checks import run_visual_checks

        visual_dir = output_dir / "visual"
        render_report = render_docx_to_png(output_docx, visual_dir)
        if render_report.status == "pass":
            page_count = render_report.page_count
            png_paths = render_report.png_paths
            visual_findings = run_visual_checks(png_paths)
            visual_finding_count = len(visual_findings)

    status: Literal["success", "ai_failed", "build_failed", "validation_warnings"] = "success"
    if val_errors > 0:
        status = "validation_warnings"

    return GenerateReport(
        run_id=run_id, status=status, output_docx=output_docx,
        page_count=page_count, png_paths=png_paths,
        ai_model=resolved_model, ai_tokens=total_tokens,
        validation_errors=val_errors, validation_warnings=val_warnings,
        visual_findings=visual_finding_count,
    )
