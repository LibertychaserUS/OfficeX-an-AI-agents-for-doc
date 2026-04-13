from __future__ import annotations

from pathlib import Path

import yaml

from .models import (
    BuildSourceManifest,
    FiguresManifest,
    ImageBlockSpec,
    ParagraphBlockSpec,
    SectionsManifest,
    SnippetsManifest,
)
from .paths import SCAFFOLD_ROOT
from .snippet_compiler import compile_snippets_for_section


class SectionAssemblyError(ValueError):
    pass


def resolve_section_source_path(source_path: Path, *, scaffold_root: Path = SCAFFOLD_ROOT) -> Path:
    if source_path.is_absolute():
        return source_path
    return (scaffold_root / source_path).resolve()


def resolve_figure_image_path(image_path: Path, *, scaffold_root: Path = SCAFFOLD_ROOT) -> Path:
    if image_path.is_absolute():
        return image_path
    return (scaffold_root / image_path).resolve()


def split_section_paragraphs(text: str, *, split_mode: str = "blank_lines") -> list[str]:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []
    if split_mode != "blank_lines":
        raise SectionAssemblyError(f"Unsupported split mode `{split_mode}`.")
    return [chunk.strip().replace("\n", " ") for chunk in normalized.split("\n\n") if chunk.strip()]


def assemble_sections_manifest(
    sections_manifest: SectionsManifest,
    *,
    figures_manifest: FiguresManifest | None = None,
    snippets_manifest: SnippetsManifest | None = None,
    scaffold_root: Path = SCAFFOLD_ROOT,
) -> BuildSourceManifest:
    blocks: list[dict] = []
    remaining_figures = sorted(
        list((figures_manifest.managed_figures if figures_manifest else [])),
        key=lambda figure: (figure.target_section_id, figure.order, figure.figure_id),
    )
    remaining_snippets = sorted(
        list((snippets_manifest.managed_snippets if snippets_manifest else [])),
        key=lambda snippet: (snippet.target_section_id, snippet.order, snippet.snippet_id),
    )

    for section in sections_manifest.managed_sections:
        if section.include_title:
            blocks.append(
                ParagraphBlockSpec(
                    role=section.title_role,
                    text=section.title,
                ).model_dump(mode="json")
            )

        source_path = resolve_section_source_path(section.source_path, scaffold_root=scaffold_root)
        if not source_path.exists():
            raise SectionAssemblyError(
                f"Section source for `{section.section_id}` is missing: `{source_path}`."
            )

        section_text = source_path.read_text(encoding="utf-8")
        paragraphs = split_section_paragraphs(section_text, split_mode=section.split_mode)
        if not paragraphs:
            raise SectionAssemblyError(
                f"Section source for `{section.section_id}` is empty after parsing: `{source_path}`."
            )

        for paragraph_text in paragraphs:
            blocks.append(
                ParagraphBlockSpec(
                    role=section.paragraph_role,
                    text=paragraph_text,
                ).model_dump(mode="json")
            )

        matching_figures = [
            figure for figure in remaining_figures if figure.target_section_id == section.section_id
        ]
        matching_snippets = [
            snippet for snippet in remaining_snippets if snippet.target_section_id == section.section_id
        ]
        compiled_assets: list[tuple[int, int, dict | list[dict]]] = []
        for figure in matching_figures:
            image_path = resolve_figure_image_path(figure.image_path, scaffold_root=scaffold_root)
            if not image_path.exists():
                raise SectionAssemblyError(
                    f"Figure asset for `{figure.figure_id}` is missing: `{image_path}`."
                )
            if figure.placement != "after_section":
                raise SectionAssemblyError(
                    f"Unsupported figure placement `{figure.placement}` for `{figure.figure_id}`."
                )
            compiled_assets.append(
                (
                    figure.order,
                    0,
                    ImageBlockSpec(
                        role=figure.role,
                        image_path=image_path,
                        caption=figure.caption,
                    ).model_dump(mode="json"),
                )
            )

        for snippet in matching_snippets:
            compiled_assets.append(
                (
                    snippet.order,
                    1,
                    compile_snippets_for_section(
                        SnippetsManifest(managed_snippets=[snippet]),
                        section_id=section.section_id,
                        scaffold_root=scaffold_root,
                    ),
                )
            )

        for _, _, payload in sorted(compiled_assets, key=lambda item: (item[0], item[1])):
            if isinstance(payload, list):
                blocks.extend(payload)
            else:
                blocks.append(payload)

        remaining_figures = [
            figure for figure in remaining_figures if figure.target_section_id != section.section_id
        ]
        remaining_snippets = [
            snippet for snippet in remaining_snippets if snippet.target_section_id != section.section_id
        ]

    if remaining_figures:
        missing_targets = ", ".join(
            f"{figure.figure_id}->{figure.target_section_id}" for figure in remaining_figures
        )
        raise SectionAssemblyError(
            "Some figures reference unknown sections: "
            f"{missing_targets}."
        )
    if remaining_snippets:
        missing_targets = ", ".join(
            f"{snippet.snippet_id}->{snippet.target_section_id}" for snippet in remaining_snippets
        )
        raise SectionAssemblyError(
            "Some snippets reference unknown sections: "
            f"{missing_targets}."
        )

    return BuildSourceManifest(
        document_id=sections_manifest.document_id,
        output_name=sections_manifest.output_name,
        blocks=blocks,
    )


def write_build_source_yaml(build_source: BuildSourceManifest, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(build_source.model_dump(mode="json"), sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
