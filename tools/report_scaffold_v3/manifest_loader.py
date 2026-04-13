from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from .models import (
    AgentCatalogManifest,
    BaselineManifest,
    BuildSourceManifest,
    CitationsManifest,
    FiguresManifest,
    LayoutContractManifest,
    NavigationCatalogManifest,
    ParagraphBlockSpec,
    ProviderCatalogManifest,
    SectionsManifest,
    SnippetsManifest,
    TemplateProfileManifest,
    WriteContractManifest,
)
from .paths import (
    DEFAULT_AGENT_CATALOG_MANIFEST,
    DEFAULT_CITATIONS_MANIFEST,
    DEFAULT_BASELINE_MANIFEST,
    DEFAULT_BUILD_SOURCE,
    DEFAULT_FIGURES_MANIFEST,
    DEFAULT_LAYOUT_CONTRACT_MANIFEST,
    DEFAULT_NAVIGATION_CATALOG,
    DEFAULT_PROVIDER_CATALOG_MANIFEST,
    DEFAULT_SECTIONS_MANIFEST,
    DEFAULT_SNIPPETS_MANIFEST,
    DEFAULT_TEMPLATE_PROFILE_MANIFEST,
    DEFAULT_WRITE_CONTRACT_MANIFEST,
)

ModelType = TypeVar("ModelType", bound=BaseModel)


def _load_yaml_model(path: Path, model_type: type[ModelType]) -> ModelType:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return model_type.model_validate(raw)


def load_baseline_manifest(path: Path = DEFAULT_BASELINE_MANIFEST) -> BaselineManifest:
    return _load_yaml_model(path, BaselineManifest)


def load_sections_manifest() -> SectionsManifest:
    return _load_yaml_model(DEFAULT_SECTIONS_MANIFEST, SectionsManifest)


def load_figures_manifest(path: Path = DEFAULT_FIGURES_MANIFEST) -> FiguresManifest:
    return _load_yaml_model(path, FiguresManifest)


def load_snippets_manifest(path: Path = DEFAULT_SNIPPETS_MANIFEST) -> SnippetsManifest:
    return _load_yaml_model(path, SnippetsManifest)


def load_citations_manifest(path: Path = DEFAULT_CITATIONS_MANIFEST) -> CitationsManifest:
    return _load_yaml_model(path, CitationsManifest)


def load_navigation_catalog(
    path: Path = DEFAULT_NAVIGATION_CATALOG,
) -> NavigationCatalogManifest:
    return _load_yaml_model(path, NavigationCatalogManifest)


def load_agent_catalog(
    path: Path = DEFAULT_AGENT_CATALOG_MANIFEST,
) -> AgentCatalogManifest:
    return _load_yaml_model(path, AgentCatalogManifest)


def load_provider_catalog(
    path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST,
) -> ProviderCatalogManifest:
    return _load_yaml_model(path, ProviderCatalogManifest)


def load_template_profile() -> TemplateProfileManifest:
    return _load_yaml_model(DEFAULT_TEMPLATE_PROFILE_MANIFEST, TemplateProfileManifest)


def load_layout_contract() -> LayoutContractManifest:
    return _load_yaml_model(DEFAULT_LAYOUT_CONTRACT_MANIFEST, LayoutContractManifest)


def load_write_contract(
    path: Path = DEFAULT_WRITE_CONTRACT_MANIFEST,
) -> WriteContractManifest:
    return _load_yaml_model(path, WriteContractManifest)


def load_build_source(path: Path = DEFAULT_BUILD_SOURCE) -> BuildSourceManifest:
    return _load_yaml_model(path, BuildSourceManifest)


def load_paragraph_blocks(path: Path = DEFAULT_BUILD_SOURCE) -> list[ParagraphBlockSpec]:
    source = load_build_source(path)
    return [
        ParagraphBlockSpec.model_validate(block)
        for block in source.blocks
        if block.get("kind") == "paragraph"
    ]
