from __future__ import annotations

import re
from pathlib import Path

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


def compose_officex_prompt(role: str, *, include_cognition: bool = True) -> str:
    parts = []
    if include_cognition:
        parts.append(load_officex_cognition())
    parts.append(load_role_prompt(role))
    return "\n\n".join(part for part in parts if part).strip() + "\n"
