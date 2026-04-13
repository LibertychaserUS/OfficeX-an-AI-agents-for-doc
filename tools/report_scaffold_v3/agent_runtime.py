from __future__ import annotations

from pathlib import Path

from .manifest_loader import load_agent_catalog
from .models import AgentCatalogEntryManifest, AgentCatalogManifest
from .paths import DEFAULT_AGENT_CATALOG_MANIFEST


def load_agent_catalog_manifest(
    catalog_path: Path = DEFAULT_AGENT_CATALOG_MANIFEST,
) -> AgentCatalogManifest:
    return load_agent_catalog(catalog_path)


def list_agent_entries(
    catalog_path: Path = DEFAULT_AGENT_CATALOG_MANIFEST,
) -> list[AgentCatalogEntryManifest]:
    return list(load_agent_catalog_manifest(catalog_path).agents)


def list_agent_ids(catalog_path: Path = DEFAULT_AGENT_CATALOG_MANIFEST) -> list[str]:
    return [entry.agent_id for entry in list_agent_entries(catalog_path)]


def get_agent_entry(
    agent_id: str,
    *,
    catalog_path: Path = DEFAULT_AGENT_CATALOG_MANIFEST,
) -> AgentCatalogEntryManifest:
    for entry in list_agent_entries(catalog_path):
        if entry.agent_id == agent_id:
            return entry
    raise ValueError(f"Unknown OfficeX agent `{agent_id}`.")
