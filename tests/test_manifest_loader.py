from tools.report_scaffold_v3.manifest_loader import (
    load_baseline_manifest,
    load_build_source,
    load_citations_manifest,
    load_navigation_catalog,
    load_sections_manifest,
    load_snippets_manifest,
    load_write_contract,
)
from tools.report_scaffold_v3.paths import DEFAULT_BASELINE_MANIFEST


def test_load_baseline_manifest_reads_expected_target():
    manifest = load_baseline_manifest(DEFAULT_BASELINE_MANIFEST)
    assert manifest.schema_version == 1
    assert manifest.target_docx.name.endswith(".docx")


def test_load_write_contract_reads_paragraph_roles():
    manifest = load_write_contract()
    assert manifest.schema_version == 1
    assert "body" in manifest.paragraph_roles
    assert manifest.paragraph_roles["body"].style == "Normal"


def test_load_build_source_reads_demo_blocks():
    source = load_build_source()
    assert source.document_id == "minimal-writer-demo"
    assert len(source.blocks) == 6


def test_load_sections_manifest_reads_managed_sections():
    manifest = load_sections_manifest()
    assert manifest.document_id == "section-assembled-demo"
    assert len(manifest.managed_sections) == 3


def test_load_snippets_manifest_reads_typed_placeholder_manifest():
    manifest = load_snippets_manifest()
    assert manifest.schema_version == 1
    assert manifest.managed_snippets == []
    assert manifest.notes


def test_load_citations_manifest_reads_typed_placeholder_manifest():
    manifest = load_citations_manifest()
    assert manifest.schema_version == 1
    assert manifest.managed_citations == []
    assert manifest.notes


def test_load_navigation_catalog_reads_indexed_entities():
    manifest = load_navigation_catalog()
    assert manifest.schema_version == 1
    assert manifest.catalog_id == "document-ops-system-navigation-catalog"
    assert any(entity.entity_id == "document_ops_system" for entity in manifest.entities)
