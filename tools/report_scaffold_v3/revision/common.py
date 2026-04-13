from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha1, sha256
import json
from pathlib import Path
from typing import Iterable, Union

import yaml
from pydantic import BaseModel

from ..docx_inspector import normalize_text


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_run_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def compute_file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def short_fingerprint(text: str) -> str:
    normalized = normalize_text(text)
    return sha1(normalized.encode("utf-8")).hexdigest()[:12]


def summarize_text(text: str, *, limit: int = 180) -> str:
    normalized = normalize_text(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def write_json(path: Path, payload: Union[dict, list]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_yaml(path: Path, payload: Union[dict, list]) -> None:
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def load_yaml_model(path: Path, model_type: type[BaseModel]) -> BaseModel:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return model_type.model_validate(raw)


def load_json_model(path: Path, model_type: type[BaseModel]) -> BaseModel:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return model_type.model_validate(raw)


def render_context_lines(lines: Iterable[str]) -> str:
    values = [line for line in lines if line]
    if not values:
        return "[none]"
    return " | ".join(values)
