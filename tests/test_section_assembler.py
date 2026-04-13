from pathlib import Path

import yaml
from PIL import Image

from tools.report_scaffold_v3.manifest_loader import load_sections_manifest
from tools.report_scaffold_v3.models import (
    FiguresManifest,
    ManagedFigureManifest,
    ManagedSnippetManifest,
    SnippetsManifest,
)
from tools.report_scaffold_v3.section_assembler import (
    assemble_sections_manifest,
    split_section_paragraphs,
    write_build_source_yaml,
)


def test_split_section_paragraphs_uses_blank_lines():
    paragraphs = split_section_paragraphs("First paragraph.\n\nSecond paragraph.")
    assert paragraphs == ["First paragraph.", "Second paragraph."]


def test_assemble_sections_manifest_builds_expected_blocks():
    manifest = load_sections_manifest()
    build_source = assemble_sections_manifest(manifest)

    assert build_source.document_id == "section-assembled-demo"
    assert build_source.output_name == "section_assembled_demo.docx"
    assert len(build_source.blocks) == 6
    assert build_source.blocks[0]["role"] == "heading_1"
    assert build_source.blocks[1]["role"] == "body"
    assert build_source.blocks[-2]["text"] == "Appendix - Platform Placeholder"


def test_write_build_source_yaml_writes_valid_yaml(tmp_path: Path):
    manifest = load_sections_manifest()
    build_source = assemble_sections_manifest(manifest)
    output_path = tmp_path / "assembled.yml"

    write_build_source_yaml(build_source, output_path)

    payload = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    assert payload["document_id"] == "section-assembled-demo"
    assert len(payload["blocks"]) == 6


def test_assemble_sections_manifest_inserts_figure_blocks_after_target_section(tmp_path: Path):
    image_path = tmp_path / "figure.png"
    Image.new("RGB", (24, 24), color="white").save(image_path)

    manifest = load_sections_manifest()
    figures_manifest = FiguresManifest(
        managed_figures=[
            ManagedFigureManifest(
                figure_id="FIG-DEMO-01",
                caption="Figure 1. Demo screenshot.",
                image_path=image_path,
                target_section_id="assembly-demo",
                order=1,
            )
        ]
    )

    build_source = assemble_sections_manifest(manifest, figures_manifest=figures_manifest)

    assert len(build_source.blocks) == 7
    assert build_source.blocks[4]["kind"] == "image"
    assert build_source.blocks[4]["caption"] == "Figure 1. Demo screenshot."


def test_assemble_sections_manifest_inserts_snippet_blocks_after_target_section():
    manifest = load_sections_manifest()
    snippets_manifest = SnippetsManifest(
        managed_snippets=[
            ManagedSnippetManifest(
                snippet_id="SNIP-DEMO-01",
                title="Demo Snippet",
                language="python",
                source_path=Path("unused.py"),
                target_section_id="assembly-demo",
                extract_mode="literal_text",
                literal_text="print('demo')",
                order=1,
            )
        ]
    )

    build_source = assemble_sections_manifest(manifest, snippets_manifest=snippets_manifest)

    assert len(build_source.blocks) == 8
    assert build_source.blocks[4]["kind"] == "paragraph"
    assert build_source.blocks[4]["text"] == "Snippet SNIP-DEMO-01 - Demo Snippet (python)"
    assert build_source.blocks[5]["text"] == "print('demo')"
