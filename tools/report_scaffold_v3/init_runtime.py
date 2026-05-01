"""OfficeX workspace initialization: officex init.

Creates a standard workspace structure so users can start using
OfficeX without cloning the full repository.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .profile_runtime import PROFILES_DIR, list_profiles, create_profile


DEFAULT_OUTLINE = """\
title: "My Document"
sections:
  - section_id: introduction
    heading: "Introduction"
    requirements: "Introduce the topic and set context."
    max_tokens: 1500

  - section_id: main_content
    heading: "Main Content"
    requirements: "Develop the core argument or information."
    max_tokens: 2000

  - section_id: conclusion
    heading: "Conclusion"
    requirements: "Summarize key points and state next steps."
    max_tokens: 1000

review_criteria:
  - "Clear and professional tone"
  - "Consistent terminology throughout"
"""


def init_workspace(
    target_dir: Path,
    *,
    profile_id: str = "a4_academic",
) -> dict:
    """Initialize a new OfficeX workspace in target_dir.

    Creates:
    - materials/     (user source materials)
    - outlines/      (document outlines)
    - outputs/       (generated documents)
    - outlines/example.yml (starter outline)
    """
    target_dir = target_dir.expanduser().resolve()

    if (target_dir / "outlines").exists():
        raise FileExistsError(
            f"Workspace already initialized at {target_dir} "
            "(outlines/ directory exists)"
        )

    dirs = ["materials", "outlines", "outputs"]
    for d in dirs:
        (target_dir / d).mkdir(parents=True, exist_ok=True)

    # Write example outline
    example_path = target_dir / "outlines" / "example.yml"
    example_path.write_text(DEFAULT_OUTLINE, encoding="utf-8")

    return {
        "workspace_path": str(target_dir),
        "profile": profile_id,
        "directories_created": dirs,
        "example_outline": str(example_path),
    }
