from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha1, sha256
from typing import Iterable

from ..docx_inspector import normalize_text


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_exec_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}"


def compute_file_sha256(path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def short_fingerprint(text: str) -> str:
    normalized = normalize_text(text)
    return sha1(normalized.encode("utf-8")).hexdigest()[:12]


def summarize_text(text: str, *, limit: int = 180) -> str:
    normalized = normalize_text(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def render_context_lines(lines: Iterable[str]) -> str:
    values = [line for line in lines if line]
    if not values:
        return "[none]"
    return " | ".join(values)
