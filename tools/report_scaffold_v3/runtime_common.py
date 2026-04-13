from __future__ import annotations

import json
import re
from datetime import datetime
import json
from pathlib import Path
from typing import Iterable

import yaml
from pydantic import BaseModel, ValidationError

from .paths import IMPORTS_DIR, PROJECT_ROOT

ARCHIVE_ROOT = PROJECT_ROOT.parent / "archive"


def sanitize_runtime_identifier(value: str, *, fallback: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return sanitized or fallback


def make_local_runtime_identifier(prefix: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{stamp}"


def local_now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def write_runtime_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_runtime_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_runtime_yaml(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def write_runtime_manifest_pair(
    runtime_dir: Path,
    *,
    stem: str,
    payload: dict,
    markdown: str,
) -> tuple[Path, Path]:
    json_path = runtime_dir / f"{stem}.json"
    markdown_path = runtime_dir / f"{stem}.md"
    write_runtime_json(json_path, payload)
    write_runtime_markdown(markdown_path, markdown)
    return json_path, markdown_path


def create_runtime_tree(root_path: Path, *subdirs: str) -> dict[str, Path]:
    resolved_root = root_path.expanduser().resolve()
    resolved_root.mkdir(parents=True, exist_ok=True)
    created: dict[str, Path] = {}
    for name in subdirs:
        path = resolved_root / name
        path.mkdir(parents=True, exist_ok=True)
        created[name] = path
    return created


def load_runtime_structured_model(path: Path, model_type: type[BaseModel]) -> BaseModel:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {resolved}")
    try:
        if resolved.suffix.lower() == ".json":
            return model_type.model_validate(json.loads(resolved.read_text(encoding="utf-8")))
        raw = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
        return model_type.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid {model_type.__name__} schema: {resolved}") from exc
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Invalid {model_type.__name__} payload: {resolved}") from exc


def ensure_mutable_candidate(candidate_path: Path, *, action: str) -> Path:
    resolved = candidate_path.expanduser().resolve()
    if is_within_directory(resolved, ARCHIVE_ROOT):
        raise ValueError(f"Refusing to {action} archived reference: {resolved}")
    if is_within_directory(resolved, IMPORTS_DIR):
        raise ValueError(f"Refusing to {action} immutable import: {resolved}")
    return resolved


def resolve_runtime_artifact_dir(
    candidate_path: Path,
    *,
    runtime_subdir: str,
    artifact_id: str,
    hidden_dir_name: str,
    output_dir: Path | None = None,
) -> Path:
    if output_dir is not None:
        resolved = output_dir.expanduser().resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    resolved_candidate = candidate_path.expanduser().resolve()
    if resolved_candidate.parent.name == "candidate":
        sandbox_root = resolved_candidate.parent.parent
        runtime_dir = sandbox_root / "runtime"
        if (runtime_dir / "sandbox_manifest.json").exists():
            resolved = runtime_dir / runtime_subdir / artifact_id
            resolved.mkdir(parents=True, exist_ok=True)
            return resolved

    resolved = resolved_candidate.parent / hidden_dir_name / artifact_id
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def is_within_directory(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def render_bullet_block(lines: Iterable[str]) -> list[str]:
    values = [line for line in lines if line]
    if not values:
        return ["- [none]"]
    return [f"- {value}" for value in values]
