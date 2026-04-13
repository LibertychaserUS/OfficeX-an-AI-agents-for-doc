from __future__ import annotations

from pathlib import Path

from .models import OfficeXWorkspaceManifest
from .paths import WORKSPACES_DIR
from .runtime_common import (
    create_runtime_tree,
    local_now_iso,
    make_local_runtime_identifier,
    sanitize_runtime_identifier,
    write_runtime_manifest_pair,
)


def render_workspace_manifest_markdown(manifest: OfficeXWorkspaceManifest) -> str:
    return "\n".join(
        [
            "# OfficeX Workspace Manifest",
            "",
            f"- Workspace ID: `{manifest.workspace_id}`",
            f"- Root path: `{manifest.root_path}`",
            f"- Runtime dir: `{manifest.runtime_dir}`",
            f"- Imports dir: `{manifest.imports_dir}`",
            f"- Reports dir: `{manifest.reports_dir}`",
            f"- Sandboxes dir: `{manifest.sandboxes_dir}`",
            f"- Exports dir: `{manifest.exports_dir}`",
            f"- Active profile: `{manifest.active_profile}`",
            f"- Active page profile: `{manifest.active_page_profile}`",
            f"- Status: `{manifest.status}`",
            f"- Created at: `{manifest.created_at}`",
        ]
    )


def create_workspace(
    *,
    workspace_id: str | None = None,
    workspace_root: Path = WORKSPACES_DIR,
    active_profile: str = "docx_mvp",
    active_page_profile: str = "a4",
) -> OfficeXWorkspaceManifest:
    resolved_root = workspace_root.expanduser().resolve()
    resolved_root.mkdir(parents=True, exist_ok=True)
    final_workspace_id = sanitize_runtime_identifier(
        workspace_id or make_local_runtime_identifier("officex-workspace"),
        fallback="officex-workspace",
    )
    workspace_dir = resolved_root / final_workspace_id
    if workspace_dir.exists():
        raise FileExistsError(f"Workspace already exists: {workspace_dir}")

    created = create_runtime_tree(
        workspace_dir,
        "runtime",
        "imports",
        "reports",
        "sandboxes",
        "exports",
    )
    runtime_dir = created["runtime"]
    imports_dir = created["imports"]
    reports_dir = created["reports"]
    sandboxes_dir = created["sandboxes"]
    exports_dir = created["exports"]

    manifest = OfficeXWorkspaceManifest(
        workspace_id=final_workspace_id,
        root_path=workspace_dir,
        runtime_dir=runtime_dir,
        imports_dir=imports_dir,
        reports_dir=reports_dir,
        sandboxes_dir=sandboxes_dir,
        exports_dir=exports_dir,
        active_profile=active_profile,
        active_page_profile=active_page_profile,
        created_at=local_now_iso(),
    )
    write_runtime_manifest_pair(
        runtime_dir,
        stem="workspace_manifest",
        payload=manifest.model_dump(mode="json"),
        markdown=render_workspace_manifest_markdown(manifest),
    )
    return manifest
