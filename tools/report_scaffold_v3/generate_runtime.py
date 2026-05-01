"""OfficeX generate runtime: end-to-end document generation from prompt.

Orchestrates the full flow:
  user prompt → AI content generation → BuildSourceManifest → writer → validation → visual audit

This is the primary "one command" experience for OfficeX as both a
standalone CLI tool and a skill callable by other agents.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .manifest_loader import (
    load_baseline_manifest,
    load_layout_contract,
    load_template_profile,
    load_write_contract,
)
from .models import BuildSourceManifest, ValidationFinding, WriteContractManifest
from .paths import (
    DEFAULT_BASELINE_MANIFEST,
    DEFAULT_WRITE_CONTRACT_MANIFEST,
    SANDBOXES_DIR,
)
from .provider_adapter import ProviderDispatchResult, dispatch_envelope
from .provider_runtime import build_provider_request_envelope
from .runtime_common import make_local_runtime_identifier, sanitize_runtime_identifier
from .writer import build_word_candidate

logger = logging.getLogger(__name__)

GENERATE_SYSTEM_PROMPT_TEMPLATE = """

You are generating structured content for a document.
Return ONLY a JSON object with this exact schema:

{{
  "title": "Document Title",
  "sections": [
    {{
      "heading": "Section Heading",
      "paragraphs": ["Paragraph 1 text.", "Paragraph 2 text."]
    }}
  ]
}}

Rules:
- Return valid JSON only, no markdown fences, no explanation outside the JSON
- Each section must have a "heading" (string) and "paragraphs" (list of strings)
- Write substantive, professional content — not placeholder text
- Match the tone and depth appropriate for the document topic

Available paragraph roles in this document profile:
{available_roles}
"""


def _build_generate_system_prompt(
    role_prompt: str,
    write_contract: WriteContractManifest,
) -> str:
    """Build the system prompt with dynamically available roles."""
    roles_desc = []
    for role_name, role_spec in write_contract.paragraph_roles.items():
        roles_desc.append(f"- {role_name} (style: {role_spec.style})")
    available_roles = "\n".join(roles_desc) if roles_desc else "- body (style: Normal)"
    suffix = GENERATE_SYSTEM_PROMPT_TEMPLATE.format(available_roles=available_roles)
    return role_prompt + suffix


@dataclass
class GenerateReport:
    """Result of a full generate run."""
    run_id: str
    status: Literal["success", "ai_failed", "build_failed", "validation_warnings"]
    output_docx: Path | None = None
    page_count: int = 0
    png_paths: list[Path] = field(default_factory=list)
    ai_model: str = ""
    ai_tokens: dict | None = None
    validation_errors: int = 0
    validation_warnings: int = 0
    visual_findings: int = 0
    error_message: str = ""

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "output_docx": str(self.output_docx) if self.output_docx else None,
            "page_count": self.page_count,
            "png_paths": [str(p) for p in self.png_paths],
            "ai_model": self.ai_model,
            "ai_tokens": self.ai_tokens,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            "visual_findings": self.visual_findings,
            "error_message": self.error_message,
        }


def _parse_ai_response_to_build_source(
    response_text: str,
    *,
    document_id: str,
    output_name: str,
) -> BuildSourceManifest:
    """Parse AI JSON response into a BuildSourceManifest."""
    text = _extract_json_from_response(response_text)
    data = json.loads(text)

    blocks: list[dict] = []

    # Title
    title = data.get("title", document_id)
    blocks.append({"kind": "paragraph", "role": "heading_1", "text": title})

    # Sections
    for section in data.get("sections", []):
        heading = section.get("heading", "")
        if heading:
            blocks.append({"kind": "paragraph", "role": "heading_2", "text": heading})
        for para_text in section.get("paragraphs", []):
            if para_text.strip():
                blocks.append({"kind": "paragraph", "role": "body", "text": para_text})

    return BuildSourceManifest(
        document_id=document_id,
        output_name=output_name,
        blocks=blocks,
    )


def _extract_json_from_response(response_text: str) -> str:
    """Extract JSON from AI response, stripping markdown fences and preamble."""
    text = response_text.strip()

    # Strip ```json ... ``` fences
    if "```" in text:
        lines = text.split("\n")
        in_fence = False
        json_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                json_lines.append(line)
        if json_lines:
            text = "\n".join(json_lines).strip()

    # Try to find JSON object boundaries if there's preamble text
    if not text.startswith("{"):
        brace_start = text.find("{")
        if brace_start >= 0:
            # Find matching closing brace
            depth = 0
            for i in range(brace_start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        text = text[brace_start:i + 1]
                        break

    return text


JSON_REPAIR_PROMPT = (
    "Your previous response was not valid JSON. Please return ONLY a valid "
    "JSON object with this structure: "
    '{"title": "...", "sections": [{"heading": "...", "paragraphs": ["..."]}]}. '
    "No markdown fences, no explanation, just the JSON object. "
    "Here was your previous response that needs to be fixed:\n\n"
)


def run_generate(
    *,
    prompt: str,
    provider_id: str = "compatible_local",
    model_id: str | None = None,
    run_id: str | None = None,
    output_dir: Path | None = None,
    baseline_manifest_path: Path = DEFAULT_BASELINE_MANIFEST,
    write_contract_path: Path = DEFAULT_WRITE_CONTRACT_MANIFEST,
    include_visual_audit: bool = True,
) -> GenerateReport:
    """Run the full generate pipeline: prompt → AI → docx → validate → visual."""
    run_id = run_id or sanitize_runtime_identifier(
        make_local_runtime_identifier("gen"),
        fallback="officex-generate",
    )
    output_dir = (output_dir or SANDBOXES_DIR / run_id).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    document_id = f"officex-{run_id}"
    output_name = f"{run_id}.docx"
    output_docx = output_dir / output_name

    # ---- Step 1: Call AI provider ----
    logger.debug("Step 1: Calling AI provider for content generation")

    # Build a minimal task packet for the envelope
    from .officex_runtime import run_docx_mvp
    # We need a sandbox with task packet for the envelope builder.
    # Instead of full run_docx_mvp, create envelope directly with a
    # synthetic system prompt.
    try:
        baseline = load_baseline_manifest(baseline_manifest_path)
        write_contract = load_write_contract(write_contract_path)

        # Build system prompt from role prompt + dynamic contract info
        from .prompt_runtime import compile_officex_prompt_bundle
        prompt_bundle = compile_officex_prompt_bundle("orchestrator", include_cognition=True)
        system_prompt = _build_generate_system_prompt(
            prompt_bundle.compiled_prompt_debug, write_contract,
        )

        # Dispatch directly without full envelope (simpler path)
        from .provider_adapter import (
            _resolve_api_key,
            _resolve_base_url,
            _dispatch_openai_compatible,
            ProviderDispatchResult,
            PROVIDER_API_KEY_ENV,
        )
        import os

        api_key = os.environ.get(PROVIDER_API_KEY_ENV)
        if not api_key:
            api_key = os.environ.get(f"OFFICEX_{provider_id.upper()}_API_KEY")
        if not api_key:
            return GenerateReport(
                run_id=run_id,
                status="ai_failed",
                error_message=f"No API key. Set {PROVIDER_API_KEY_ENV}.",
            )

        base_url = os.environ.get("OFFICEX_PROVIDER_BASE_URL")

        from openai import OpenAI
        client_kwargs: dict = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = OpenAI(**client_kwargs)
        resolved_model = model_id or "qwen-plus"

        logger.debug("Dispatching to %s model=%s", provider_id, resolved_model)
        response = client.chat.completions.create(
            model=resolved_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        ai_text = response.choices[0].message.content or ""
        ai_tokens = None
        if response.usage:
            ai_tokens = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        logger.debug("AI responded: %d chars, tokens=%s", len(ai_text), ai_tokens)

    except Exception as exc:
        logger.error("AI dispatch failed: %s", exc)
        return GenerateReport(
            run_id=run_id,
            status="ai_failed",
            error_message=str(exc),
        )

    # Save raw AI response
    (output_dir / "ai_response.txt").write_text(ai_text, encoding="utf-8")

    # ---- Step 2: Parse AI response into BuildSourceManifest ----
    logger.debug("Step 2: Parsing AI response into build source")
    build_source = None
    parse_error = None

    try:
        build_source = _parse_ai_response_to_build_source(
            ai_text, document_id=document_id, output_name=output_name,
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        parse_error = exc
        logger.debug("First parse failed (%s), attempting JSON repair request", exc)

    # If first parse failed, ask AI to fix its response
    if build_source is None and parse_error is not None:
        try:
            repair_response = client.chat.completions.create(
                model=resolved_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": ai_text},
                    {"role": "user", "content": JSON_REPAIR_PROMPT + ai_text[:2000]},
                ],
                temperature=0.1,
            )
            repair_text = repair_response.choices[0].message.content or ""
            (output_dir / "ai_repair_response.txt").write_text(repair_text, encoding="utf-8")

            if repair_response.usage:
                ai_tokens = {
                    "prompt_tokens": ai_tokens.get("prompt_tokens", 0) + repair_response.usage.prompt_tokens,
                    "completion_tokens": ai_tokens.get("completion_tokens", 0) + repair_response.usage.completion_tokens,
                    "total_tokens": ai_tokens.get("total_tokens", 0) + repair_response.usage.total_tokens,
                }

            build_source = _parse_ai_response_to_build_source(
                repair_text, document_id=document_id, output_name=output_name,
            )
        except (json.JSONDecodeError, KeyError, TypeError, Exception) as exc2:
            logger.error("JSON repair also failed: %s", exc2)
            return GenerateReport(
                run_id=run_id,
                status="ai_failed",
                ai_model=resolved_model,
                ai_tokens=ai_tokens,
                error_message=f"AI response parse failed after repair attempt: {parse_error} -> {exc2}",
            )

    # Save parsed build source
    (output_dir / "build_source.json").write_text(
        json.dumps(build_source.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ---- Step 3: Generate docx ----
    logger.debug("Step 3: Building docx from parsed content")
    try:
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
        logger.debug("Built %s: %d paragraphs", output_docx.name, build_result.paragraph_count)
    except Exception as exc:
        logger.error("docx build failed: %s", exc)
        return GenerateReport(
            run_id=run_id,
            status="build_failed",
            ai_model=resolved_model,
            ai_tokens=ai_tokens,
            error_message=str(exc),
        )

    # ---- Step 4: Structural validation ----
    logger.debug("Step 4: Structural validation")
    from .docx_inspector import inspect_docx, inspect_docx_overrides
    from .ooxml_inspector import extract_effective_style_inventory
    from .validation import build_validation_report

    template_profile = load_template_profile().model_dump(mode="json")
    layout_contract = load_layout_contract().model_dump(mode="json")

    inventory = inspect_docx(output_docx)
    val_report = build_validation_report(
        output_docx,
        inventory,
        target_role="candidate_output",
        template_profile=template_profile,
        layout_contract=layout_contract,
        style_inventory=extract_effective_style_inventory(output_docx),
        override_inventory=inspect_docx_overrides(output_docx),
    )
    val_errors = sum(1 for f in val_report.findings if f.severity == "error")
    val_warnings = sum(1 for f in val_report.findings if f.severity == "warning")

    # Save validation report
    (output_dir / "validation.json").write_text(
        json.dumps(val_report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ---- Step 5: Visual audit ----
    page_count = 0
    png_paths: list[Path] = []
    visual_finding_count = 0

    if include_visual_audit:
        logger.debug("Step 5: Visual audit (render + check)")
        from .visual_audit import render_docx_to_png
        from .visual_audit_checks import run_visual_checks

        visual_dir = output_dir / "visual"
        render_report = render_docx_to_png(output_docx, visual_dir)

        if render_report.status == "pass":
            page_count = render_report.page_count
            png_paths = render_report.png_paths
            visual_findings = run_visual_checks(png_paths)
            visual_finding_count = len(visual_findings)

            (output_dir / "visual_audit.json").write_text(
                json.dumps(render_report.model_dump(mode="json"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        else:
            logger.warning("Visual audit skipped: %s", render_report.status)

    # ---- Final status ----
    status: Literal["success", "ai_failed", "build_failed", "validation_warnings"] = "success"
    if val_errors > 0:
        status = "validation_warnings"

    return GenerateReport(
        run_id=run_id,
        status=status,
        output_docx=output_docx,
        page_count=page_count,
        png_paths=png_paths,
        ai_model=resolved_model,
        ai_tokens=ai_tokens,
        validation_errors=val_errors,
        validation_warnings=val_warnings,
        visual_findings=visual_finding_count,
    )
