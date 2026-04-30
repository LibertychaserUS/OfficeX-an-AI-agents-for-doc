from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import (
    OfficeXCompiledPromptBundle,
    OfficeXPromptManifestEntry,
    OfficeXPromptTraceRecord,
    OfficeXResolvedPromptRef,
)
from .paths import PROMPTS_DIR


ROLE_PROMPT_FILES = {
    "orchestrator": PROMPTS_DIR / "ORCHESTRATOR.md",
    "template_analyst": PROMPTS_DIR / "TEMPLATE_ANALYST.md",
    "patch_engineer": PROMPTS_DIR / "PATCH_ENGINEER.md",
    "style_layout_engineer": PROMPTS_DIR / "STYLE_LAYOUT_ENGINEER.md",
    "validation_engineer": PROMPTS_DIR / "VALIDATION_ENGINEER.md",
    "test_auditor": PROMPTS_DIR / "TEST_AUDITOR.md",
}

COGNITION_PROMPT_FILE = PROMPTS_DIR / "OFFICEX_COGNITION.md"
FRONTMATTER_PATTERN = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def _read_markdown_body(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    return FRONTMATTER_PATTERN.sub("", content, count=1).strip()


def _prompt_ref(path: Path) -> str:
    return f"prompts/{path.name}"


def _extract_section_title(markdown_body: str, *, fallback: str) -> str:
    for line in markdown_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def _sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def list_officex_roles() -> list[str]:
    return sorted(ROLE_PROMPT_FILES.keys())


def load_officex_cognition() -> str:
    return _read_markdown_body(COGNITION_PROMPT_FILE)


def load_role_prompt(role: str) -> str:
    try:
        prompt_path = ROLE_PROMPT_FILES[role]
    except KeyError as exc:
        raise ValueError(f"Unknown OfficeX role prompt: `{role}`.") from exc
    return _read_markdown_body(prompt_path)


def build_officex_prompt_manifest(
    role: str,
    *,
    include_cognition: bool = True,
) -> list[OfficeXPromptManifestEntry]:
    if role not in ROLE_PROMPT_FILES:
        raise ValueError(f"Unknown OfficeX role prompt: `{role}`.")

    manifest: list[OfficeXPromptManifestEntry] = []
    if include_cognition:
        manifest.append(
            OfficeXPromptManifestEntry(
                layer="cognition",
                prompt_id="officex_cognition",
                ref=_prompt_ref(COGNITION_PROMPT_FILE),
            )
        )
    manifest.append(
        OfficeXPromptManifestEntry(
            layer="role",
            prompt_id=role,
            ref=_prompt_ref(ROLE_PROMPT_FILES[role]),
        )
    )
    return manifest


def _resolve_prompt_manifest_entry(
    entry: OfficeXPromptManifestEntry,
) -> tuple[OfficeXResolvedPromptRef, str]:
    source_path = (PROMPTS_DIR.parent / entry.ref).resolve()
    prompt_body = _read_markdown_body(source_path)
    resolved = OfficeXResolvedPromptRef(
        layer=entry.layer,
        prompt_id=entry.prompt_id,
        ref=entry.ref,
        source_path=source_path,
        section_title=_extract_section_title(prompt_body, fallback=entry.prompt_id),
        content_sha256=_sha256_text(prompt_body),
    )
    return resolved, prompt_body


def compile_officex_prompt_bundle(
    role: str,
    *,
    include_cognition: bool = True,
) -> OfficeXCompiledPromptBundle:
    manifest = build_officex_prompt_manifest(role, include_cognition=include_cognition)
    resolved_rule_refs: list[OfficeXResolvedPromptRef] = []
    prompt_parts: list[str] = []
    for entry in manifest:
        resolved, prompt_body = _resolve_prompt_manifest_entry(entry)
        resolved_rule_refs.append(resolved)
        prompt_parts.append(prompt_body)
    compiled_prompt = "\n\n".join(part for part in prompt_parts if part).strip() + "\n"
    prompt_trace_record = OfficeXPromptTraceRecord(
        role=role,
        include_cognition=include_cognition,
        prompt_source_refs=[entry.ref for entry in manifest],
        compiled_prompt_sha256=_sha256_text(compiled_prompt),
    )
    return OfficeXCompiledPromptBundle(
        role=role,
        include_cognition=include_cognition,
        prompt_manifest=manifest,
        resolved_rule_refs=resolved_rule_refs,
        compiled_prompt_debug=compiled_prompt,
        prompt_trace_record=prompt_trace_record,
    )


def compose_officex_prompt(role: str, *, include_cognition: bool = True) -> str:
    return compile_officex_prompt_bundle(
        role,
        include_cognition=include_cognition,
    ).compiled_prompt_debug
