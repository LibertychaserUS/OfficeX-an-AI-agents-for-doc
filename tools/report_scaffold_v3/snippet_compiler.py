from __future__ import annotations

from pathlib import Path

from .models import ManagedSnippetManifest, ParagraphBlockSpec, SnippetsManifest
from .paths import SCAFFOLD_ROOT


class SnippetCompilationError(ValueError):
    pass


def resolve_snippet_source_path(source_path: Path, *, scaffold_root: Path = SCAFFOLD_ROOT) -> Path:
    if source_path.is_absolute():
        return source_path
    return (scaffold_root / source_path).resolve()


def extract_snippet_text(
    snippet: ManagedSnippetManifest,
    *,
    scaffold_root: Path = SCAFFOLD_ROOT,
) -> str:
    if snippet.extract_mode == "literal_text":
        if snippet.literal_text is None:
            raise SnippetCompilationError(
                f"Snippet `{snippet.snippet_id}` requires `literal_text` for extract_mode `literal_text`."
            )
        return snippet.literal_text.strip("\n")

    source_path = resolve_snippet_source_path(snippet.source_path, scaffold_root=scaffold_root)
    if not source_path.exists():
        raise SnippetCompilationError(
            f"Snippet source for `{snippet.snippet_id}` is missing: `{source_path}`."
        )

    if snippet.start_line is None or snippet.end_line is None:
        raise SnippetCompilationError(
            f"Snippet `{snippet.snippet_id}` requires `start_line` and `end_line` for `line_range` extraction."
        )
    if snippet.start_line < 1 or snippet.end_line < snippet.start_line:
        raise SnippetCompilationError(
            f"Snippet `{snippet.snippet_id}` has invalid line range {snippet.start_line}-{snippet.end_line}."
        )

    lines = source_path.read_text(encoding="utf-8").splitlines()
    if snippet.end_line > len(lines):
        raise SnippetCompilationError(
            f"Snippet `{snippet.snippet_id}` range {snippet.start_line}-{snippet.end_line} exceeds source length {len(lines)}."
        )

    extracted = "\n".join(lines[snippet.start_line - 1 : snippet.end_line]).rstrip()
    if not extracted.strip():
        raise SnippetCompilationError(
            f"Snippet `{snippet.snippet_id}` extracted empty content from `{source_path}`."
        )
    return extracted


def render_snippet_label(snippet: ManagedSnippetManifest) -> str:
    language_suffix = f" ({snippet.language})" if snippet.language else ""
    return f"Snippet {snippet.snippet_id} - {snippet.title}{language_suffix}"


def compile_snippets_for_section(
    snippets_manifest: SnippetsManifest | None,
    *,
    section_id: str,
    scaffold_root: Path = SCAFFOLD_ROOT,
) -> list[dict]:
    if snippets_manifest is None:
        return []

    matching_snippets = sorted(
        [snippet for snippet in snippets_manifest.managed_snippets if snippet.target_section_id == section_id],
        key=lambda snippet: (snippet.order, snippet.snippet_id),
    )
    blocks: list[dict] = []
    for snippet in matching_snippets:
        if snippet.placement != "after_section":
            raise SnippetCompilationError(
                f"Unsupported snippet placement `{snippet.placement}` for `{snippet.snippet_id}`."
            )
        blocks.append(
            ParagraphBlockSpec(
                role=snippet.label_role,
                text=render_snippet_label(snippet),
            ).model_dump(mode="json")
        )
        blocks.append(
            ParagraphBlockSpec(
                role=snippet.code_role,
                text=extract_snippet_text(snippet, scaffold_root=scaffold_root),
            ).model_dump(mode="json")
        )
    return blocks
