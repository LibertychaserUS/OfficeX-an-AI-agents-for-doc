from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
import yaml

from .paths import (
    BUILDS_DIR,
    BUILD_SOURCES_DIR,
    SECTION_PIPELINE_DIR,
    CURRENT_BASELINE_DIR,
    DEFAULT_AGENT_CATALOG_MANIFEST,
    DEFAULT_BASELINE_MANIFEST,
    DEFAULT_BUILD_SOURCE,
    DEFAULT_OFFICEX_DESKTOP_SHELL_DIR,
    DEFAULT_SNIPPETS_MANIFEST,
    DEFAULT_SECTION_BUILD_SOURCE,
    DEFAULT_PROVIDER_CATALOG_MANIFEST,
    DEFAULT_WRITE_CONTRACT_MANIFEST,
    CANDIDATE_AUDIT_DIR,
    FONT_AUDIT_DIR,
    OUTLINE_AUDIT_DIR,
    PUBLISHED_DIR,
    SNIPPET_AUDIT_DIR,
    TRACE_DIR,
    VALIDATION_DIR,
    SANDBOXES_DIR,
    WORKSPACES_DIR,
)
from .package_contract import collect_package_integrity_issues, format_package_integrity_report
from .cli_render import (
    render_build_summary,
    render_candidate_audit_summary,
    render_font_audit_summary,
    render_import_summary,
    render_officex_agent_list,
    render_officex_agent_show,
    render_officex_anchor_prep_report,
    render_officex_doctor_report,
    render_officex_patch_bridge_report,
    render_officex_provider_binding,
    render_officex_provider_list,
    render_officex_provider_request,
    render_officex_render_boundary_report,
    render_officex_review_ledger,
    render_officex_sandbox_created,
    render_officex_task_packet,
    render_officex_task_run,
    render_officex_trace_checkpoint,
    render_officex_workspace_created,
    render_outline_audit_summary,
    render_published_run_summary,
    render_section_assembly_summary,
    render_section_pipeline_summary,
    render_snippet_audit_summary,
    render_trace_catalog_summary,
)

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
console = Console()
officex_app = typer.Typer(no_args_is_help=True, help="OfficeX runtime commands.")
officex_workspace_app = typer.Typer(no_args_is_help=True, help="OfficeX workspace commands.")
officex_sandbox_app = typer.Typer(no_args_is_help=True, help="OfficeX sandbox commands.")
officex_task_app = typer.Typer(no_args_is_help=True, help="OfficeX task commands.")
officex_prompt_app = typer.Typer(no_args_is_help=True, help="OfficeX prompt commands.")
officex_provider_app = typer.Typer(no_args_is_help=True, help="OfficeX provider commands.")
officex_agent_app = typer.Typer(no_args_is_help=True, help="OfficeX agent commands.")
officex_trace_app = typer.Typer(no_args_is_help=True, help="OfficeX trace commands.")
officex_audit_app = typer.Typer(no_args_is_help=True, help="OfficeX audit commands.")
officex_app.add_typer(officex_workspace_app, name="workspace")
officex_app.add_typer(officex_sandbox_app, name="sandbox")
officex_app.add_typer(officex_task_app, name="task")
officex_app.add_typer(officex_prompt_app, name="prompt")
officex_app.add_typer(officex_provider_app, name="provider")
officex_app.add_typer(officex_agent_app, name="agent")
officex_app.add_typer(officex_trace_app, name="trace")
officex_app.add_typer(officex_audit_app, name="audit")
app.add_typer(officex_app, name="officex")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_yaml(path: Path, payload: dict | list) -> None:
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def is_within_directory(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def build_summary_paths(output_docx: Path) -> tuple[Path, Path]:
    return (
        output_docx.with_suffix(".build_summary.json"),
        output_docx.with_suffix(".build_summary.md"),
    )


def section_summary_paths(output_source: Path) -> tuple[Path, Path]:
    return (
        output_source.with_suffix(".summary.json"),
        output_source.with_suffix(".summary.md"),
    )


def resolve_target_context(
    docx: Optional[Path],
    baseline_manifest_path: Path,
    explicit_target_role: Optional[str] = None,
) -> tuple[Path, str, Optional[Path]]:
    from .manifest_loader import load_baseline_manifest

    manifest = load_baseline_manifest(baseline_manifest_path)
    format_authority_docx = (
        manifest.format_authority_docx.expanduser().resolve()
        if manifest.format_authority_docx
        else None
    )

    def infer_target_role(resolved_docx: Path) -> str:
        if explicit_target_role is not None:
            return explicit_target_role
        if resolved_docx == manifest.target_docx.expanduser().resolve():
            return manifest.target_docx_role
        if format_authority_docx is not None and resolved_docx == format_authority_docx:
            return "template_authority"
        candidate_roots = [BUILDS_DIR.expanduser().resolve(), SECTION_PIPELINE_DIR.expanduser().resolve()]
        for root in candidate_roots:
            try:
                resolved_docx.relative_to(root)
                return "candidate_output"
            except ValueError:
                continue
        return "ad_hoc"

    if docx is not None:
        resolved_docx = docx.expanduser().resolve()
        return (resolved_docx, infer_target_role(resolved_docx), format_authority_docx)
    return (
        manifest.target_docx.expanduser().resolve(),
        explicit_target_role or manifest.target_docx_role,
        format_authority_docx,
    )




def resolve_revision_run_dir(run_dir: Path) -> Path:
    resolved = run_dir.expanduser().resolve()
    ensure_dir(resolved)
    return resolved


def ensure_safe_candidate_output(output_docx: Path, *, baseline_manifest) -> None:
    resolved_output = output_docx.expanduser().resolve()
    protected_paths = [baseline_manifest.target_docx.expanduser().resolve()]
    if baseline_manifest.format_authority_docx is not None:
        protected_paths.append(baseline_manifest.format_authority_docx.expanduser().resolve())

    for protected_path in protected_paths:
        if resolved_output == protected_path:
            raise typer.BadParameter(
                f"Refusing to write candidate output over protected file `{protected_path}`."
            )

    for root in baseline_manifest.read_only_reference_roots:
        resolved_root = root.expanduser().resolve()
        try:
            resolved_output.relative_to(resolved_root)
        except ValueError:
            continue
        raise typer.BadParameter(
            f"Refusing to write candidate output inside read-only reference root `{resolved_root}`."
        )


@app.callback()
def preflight() -> None:
    issues = collect_package_integrity_issues()
    if issues:
        console.print(f"[bold red]{format_package_integrity_report(issues)}[/bold red]")
        raise typer.Exit(code=2)


@app.command("show-config")
def show_config(
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
) -> None:
    from .manifest_loader import load_baseline_manifest

    manifest = load_baseline_manifest(baseline_manifest)
    console.print(f"Project root: {manifest.scaffold_root}")
    console.print(f"Target docx: {manifest.target_docx}")
    console.print(f"Target role: {manifest.target_docx_role}")
    console.print(f"Formatting authority: {manifest.format_authority_docx}")
    console.print("Read-only references:")
    for root in manifest.read_only_reference_roots:
        console.print(f"  - {root}")


@app.command("import-baseline")
def import_baseline(
    docx: Optional[Path] = typer.Option(
        None,
        "--docx",
        help="Optional explicit target docx. Defaults to manifests/baseline.yml",
    ),
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
    output_dir: Path = typer.Option(
        CURRENT_BASELINE_DIR,
        "--output-dir",
        help="Directory for generated baseline inventory files.",
    ),
) -> None:
    from .docx_inspector import inspect_docx

    target_docx, target_role, format_authority_docx = resolve_target_context(
        docx, baseline_manifest
    )
    ensure_dir(output_dir)

    inventory = inspect_docx(target_docx)

    write_json(output_dir / "inventory.json", inventory)
    write_json(output_dir / "headings.json", inventory["headings"])
    write_json(output_dir / "figures.json", inventory["figures"])
    write_json(output_dir / "paragraph_fingerprints.json", inventory["paragraph_fingerprints"])
    write_markdown(
        output_dir / "baseline_diagnostic.md",
        render_import_summary(
            inventory,
            target_role=target_role,
            format_authority_docx=format_authority_docx,
        ),
    )

    console.print(f"Imported baseline from {target_docx}")
    console.print(f"Wrote inventory to {output_dir}")


@app.command("validate-word")
def validate_word(
    docx: Optional[Path] = typer.Option(
        None,
        "--docx",
        help="Optional explicit target docx. Defaults to manifests/baseline.yml",
    ),
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
    target_role: Optional[str] = typer.Option(
        None,
        "--target-role",
        help="Optional explicit target role: reference_sample, template_authority, candidate_output, or ad_hoc.",
    ),
    output_dir: Path = typer.Option(
        VALIDATION_DIR,
        "--output-dir",
        help="Directory for generated validation reports.",
    ),
) -> None:
    from .docx_inspector import inspect_docx, inspect_docx_overrides
    from .manifest_loader import load_layout_contract, load_template_profile
    from .ooxml_inspector import extract_effective_style_inventory
    from .validation import build_validation_report, render_validation_markdown

    target_docx, target_role, format_authority_docx = resolve_target_context(
        docx, baseline_manifest, target_role
    )
    ensure_dir(output_dir)

    inventory = inspect_docx(target_docx)
    override_inventory = inspect_docx_overrides(target_docx)
    template_profile = load_template_profile().model_dump(mode="json")
    layout_contract = load_layout_contract().model_dump(mode="json")
    style_inventory = extract_effective_style_inventory(target_docx)

    report = build_validation_report(
        target_docx,
        inventory,
        target_role=target_role,
        format_authority_docx=format_authority_docx,
        template_profile=template_profile,
        layout_contract=layout_contract,
        style_inventory=style_inventory,
        override_inventory=override_inventory,
    )

    write_json(output_dir / "validation.json", report.model_dump(mode="json"))
    write_markdown(output_dir / "validation_report.md", render_validation_markdown(report))

    error_count = sum(1 for finding in report.findings if finding.severity == "error")
    warning_count = sum(1 for finding in report.findings if finding.severity == "warning")
    console.print(
        f"Validated {target_docx} as {target_role} with {error_count} error(s) and {warning_count} warning(s)."
    )


@app.command("build-word")
def build_word(
    source: Path = typer.Option(
        DEFAULT_BUILD_SOURCE,
        "--source",
        help="Structured build source for a minimal candidate docx.",
    ),
    write_contract: Path = typer.Option(
        DEFAULT_WRITE_CONTRACT_MANIFEST,
        "--write-contract",
        help="Write contract YAML.",
    ),
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
    output_docx: Optional[Path] = typer.Option(
        None,
        "--output-docx",
        help="Optional explicit candidate output path.",
    ),
) -> None:
    from .manifest_loader import load_baseline_manifest, load_build_source, load_write_contract
    from .writer import build_word_candidate

    baseline = load_baseline_manifest(baseline_manifest)
    template_docx = (
        baseline.format_authority_docx.expanduser().resolve()
        if baseline.format_authority_docx
        else baseline.target_docx.expanduser().resolve()
    )
    source_manifest = load_build_source(source)
    write_contract_manifest = load_write_contract(write_contract)

    resolved_output = output_docx
    if resolved_output is None:
        resolved_output = BUILDS_DIR / source_manifest.output_name
    resolved_output = resolved_output.expanduser().resolve()
    ensure_safe_candidate_output(resolved_output, baseline_manifest=baseline)

    result = build_word_candidate(
        template_docx=template_docx,
        source=source_manifest,
        contract=write_contract_manifest,
        output_docx=resolved_output,
    )

    build_payload = result.model_dump(mode="json")
    summary_json_path, summary_markdown_path = build_summary_paths(resolved_output)
    write_json(summary_json_path, build_payload)
    write_markdown(summary_markdown_path, render_build_summary(build_payload))

    if is_within_directory(resolved_output, BUILDS_DIR):
        ensure_dir(BUILDS_DIR)
        write_json(BUILDS_DIR / "build_summary.json", build_payload)
        write_markdown(BUILDS_DIR / "build_summary.md", render_build_summary(build_payload))

    console.print(f"Built candidate docx at {resolved_output}")


@app.command("check-package")
def check_package() -> None:
    issues = collect_package_integrity_issues()
    if issues:
        console.print(format_package_integrity_report(issues))
        raise typer.Exit(code=1)
    console.print("OfficeX runtime package integrity check passed.")


@officex_workspace_app.command("init")
def officex_workspace_init(
    workspace_id: Optional[str] = typer.Option(
        None,
        "--workspace-id",
        help="Optional explicit OfficeX workspace id.",
    ),
    workspace_root: Path = typer.Option(
        WORKSPACES_DIR,
        "--workspace-root",
        help="Root directory for OfficeX workspaces.",
    ),
    active_profile: str = typer.Option(
        "docx_mvp",
        "--active-profile",
        help="Active profile name for the workspace.",
    ),
    active_page_profile: str = typer.Option(
        "a4",
        "--active-page-profile",
        help="Active page profile for the workspace.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .workspace_runtime import create_workspace

    try:
        manifest = create_workspace(
            workspace_id=workspace_id,
            workspace_root=workspace_root.expanduser().resolve(),
            active_profile=active_profile,
            active_page_profile=active_page_profile,
        )
    except FileExistsError as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc
    payload = manifest.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_workspace_created(payload))


@officex_sandbox_app.command("create")
def officex_sandbox_create(
    run_id: Optional[str] = typer.Option(
        None,
        "--run-id",
        help="Optional explicit sandbox run id.",
    ),
    sandbox_root: Path = typer.Option(
        SANDBOXES_DIR,
        "--sandbox-root",
        help="Root directory for OfficeX sandboxes.",
    ),
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .officex_runtime import create_docx_mvp_sandbox

    try:
        manifest = create_docx_mvp_sandbox(
            run_id=run_id,
            sandbox_root=sandbox_root.expanduser().resolve(),
            baseline_manifest_path=baseline_manifest.expanduser().resolve(),
        )
    except FileExistsError as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc
    payload = manifest.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_sandbox_created(manifest.run_id, manifest.sandbox_root))


@officex_app.command("doctor")
def officex_doctor(
    workspace_root: Path = typer.Option(
        WORKSPACES_DIR / "default",
        "--workspace-root",
        help="Workspace root used for environment readiness checks.",
    ),
    sandbox_root: Path = typer.Option(
        SANDBOXES_DIR,
        "--sandbox-root",
        help="Sandbox root used for smoke and boundary checks.",
    ),
    desktop_shell_dir: Path = typer.Option(
        DEFAULT_OFFICEX_DESKTOP_SHELL_DIR,
        "--desktop-shell-dir",
        help="Desktop shell directory used by the OfficeX app launcher.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .doctor_runtime import build_doctor_report, persist_doctor_report

    report = persist_doctor_report(
        build_doctor_report(
        workspace_root=workspace_root.expanduser().resolve(),
        sandbox_root=sandbox_root.expanduser().resolve(),
        desktop_shell_dir=desktop_shell_dir.expanduser().resolve(),
        )
    )
    payload = report.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_doctor_report(payload))


@officex_app.command("render-boundary")
def officex_render_boundary(
    workspace_root: Path = typer.Option(
        WORKSPACES_DIR / "default",
        "--workspace-root",
        help="Workspace root used for generated boundary fixtures.",
    ),
    sandbox_root: Path = typer.Option(
        SANDBOXES_DIR,
        "--sandbox-root",
        help="Sandbox root used for render-boundary runs.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .render_boundary_runtime import (
        build_render_boundary_report,
        persist_render_boundary_report,
    )

    report = persist_render_boundary_report(
        build_render_boundary_report(
            workspace_root=workspace_root.expanduser().resolve(),
            sandbox_root=sandbox_root.expanduser().resolve(),
        )
    )
    payload = report.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_render_boundary_report(payload))


@officex_task_app.command("run-docx-mvp")
def officex_task_run_docx_mvp(
    run_id: Optional[str] = typer.Option(
        None,
        "--run-id",
        help="Optional explicit run id.",
    ),
    sandbox_root: Path = typer.Option(
        SANDBOXES_DIR,
        "--sandbox-root",
        help="Root directory for OfficeX sandboxes.",
    ),
    source: Path = typer.Option(
        DEFAULT_BUILD_SOURCE,
        "--source",
        help="Structured build source used for the MVP run.",
    ),
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
    write_contract: Path = typer.Option(
        DEFAULT_WRITE_CONTRACT_MANIFEST,
        "--write-contract",
        help="Path to the write contract YAML.",
    ),
    approval_mode: str = typer.Option(
        "ask_every_conflict",
        "--approval-mode",
        help="Approval mode for the runtime task packet.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .officex_runtime import run_docx_mvp

    try:
        report = run_docx_mvp(
            run_id=run_id,
            sandbox_root=sandbox_root.expanduser().resolve(),
            source_path=source.expanduser().resolve(),
            baseline_manifest_path=baseline_manifest.expanduser().resolve(),
            write_contract_path=write_contract.expanduser().resolve(),
            approval_mode=approval_mode,
        )
    except FileExistsError as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc
    payload = report.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_task_run(payload))


@officex_task_app.command("inspect")
def officex_task_inspect(
    task_packet: Optional[Path] = typer.Option(
        None,
        "--task-packet",
        help="Explicit path to a task_packet.json file.",
    ),
    run_id: Optional[str] = typer.Option(
        None,
        "--run-id",
        help="Sandbox run id used to resolve runtime/task_packet.json.",
    ),
    sandbox_root: Path = typer.Option(
        SANDBOXES_DIR,
        "--sandbox-root",
        help="Root directory for OfficeX sandboxes.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .officex_runtime import load_task_packet

    try:
        packet = load_task_packet(
            task_packet_path=task_packet,
            run_id=run_id,
            sandbox_root=sandbox_root.expanduser().resolve(),
        )
    except (ValueError, FileNotFoundError) as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc

    payload = packet.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_task_packet(payload))


@officex_task_app.command("build-review-ledger")
def officex_task_build_review_ledger(
    review_findings: Path = typer.Option(
        ...,
        "--review-findings",
        help="Structured manual review JSON/YAML input.",
    ),
    output_path: Optional[Path] = typer.Option(
        None,
        "--output-path",
        help="Optional explicit output path for the normalized OfficeX review ledger JSON.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .review_runtime import build_review_ledger

    try:
        ledger, resolved_output_path = build_review_ledger(
            review_input_path=review_findings,
            output_path=output_path,
        )
    except (ValueError, FileNotFoundError) as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc

    payload = ledger.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_review_ledger(payload, output_path=resolved_output_path))


@officex_task_app.command("extract-anchors")
def officex_task_extract_anchors(
    candidate_docx: Path = typer.Option(
        ...,
        "--candidate-docx",
        help="Candidate docx to inspect for OfficeX live anchors.",
    ),
    review_ledger: Path = typer.Option(
        ...,
        "--review-ledger",
        help="Normalized OfficeX review ledger JSON/YAML file.",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        help="Optional explicit output directory for review prep artifacts.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .review_runtime import extract_anchors_from_review_ledger

    try:
        report = extract_anchors_from_review_ledger(
            candidate_path=candidate_docx,
            review_ledger_path=review_ledger,
            output_dir=output_dir,
        )
    except (ValueError, FileNotFoundError) as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc

    payload = report.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        console.print(render_officex_anchor_prep_report(payload))
    if payload["finding_count"] > 0:
        raise typer.Exit(code=1)


@officex_task_app.command("apply-patch-bundle")
def officex_task_apply_patch_bundle(
    patch_bundle: Path = typer.Option(
        ...,
        "--patch-bundle",
        help="Path to an OfficeX patch bundle JSON/YAML file.",
    ),
    candidate_docx: Path = typer.Option(
        ...,
        "--candidate-docx",
        help="Candidate docx to mutate through the deterministic OfficeX patch bridge.",
    ),
    anchor_snapshot: Path = typer.Option(
        ...,
        "--anchor-snapshot",
        help="Revision live anchor snapshot JSON/YAML file.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--apply",
        help="Validate through the deterministic bridge without mutating, or apply in place.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .patch_bridge_runtime import apply_officex_patch_bundle

    try:
        report = apply_officex_patch_bundle(
            patch_bundle_path=patch_bundle.expanduser().resolve(),
            candidate_path=candidate_docx.expanduser().resolve(),
            anchor_snapshot_path=anchor_snapshot.expanduser().resolve(),
            dry_run=dry_run,
        )
    except (ValueError, FileNotFoundError) as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc

    payload = report.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        console.print(render_officex_patch_bridge_report(payload))
    if payload["status"] == "failed":
        raise typer.Exit(code=1)


@officex_prompt_app.command("show")
def officex_prompt_show(
    role: str = typer.Option(
        ...,
        "--role",
        help="OfficeX role prompt id.",
    ),
    include_cognition: bool = typer.Option(
        True,
        "--include-cognition/--role-only",
        help="Include the OfficeX cognition layer before the role prompt.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of raw prompt text.",
    ),
) -> None:
    from .prompt_runtime import compose_officex_prompt, list_officex_roles

    if role not in list_officex_roles():
        console.print(f"Unknown OfficeX role `{role}`. Available roles: {', '.join(list_officex_roles())}")
        raise typer.Exit(code=1)

    prompt = compose_officex_prompt(role, include_cognition=include_cognition)
    if as_json:
        console.print_json(
            json.dumps(
                {
                    "role": role,
                    "include_cognition": include_cognition,
                    "prompt": prompt,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    console.print(prompt)


@officex_provider_app.command("list")
def officex_provider_list(
    catalog_path: Path = typer.Option(
        DEFAULT_PROVIDER_CATALOG_MANIFEST,
        "--catalog-path",
        help="Path to the OfficeX provider catalog YAML.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .provider_runtime import load_provider_catalog_manifest

    catalog = load_provider_catalog_manifest(catalog_path.expanduser().resolve())
    payload = catalog.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_provider_list(payload))


@officex_provider_app.command("show")
def officex_provider_show(
    provider: str = typer.Option(
        ...,
        "--provider",
        help="OfficeX provider id.",
    ),
    role: str = typer.Option(
        "orchestrator",
        "--role",
        help="OfficeX role prompt id.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        help="Optional explicit provider model id.",
    ),
    include_cognition: bool = typer.Option(
        True,
        "--include-cognition/--role-only",
        help="Include the OfficeX cognition layer before the role prompt.",
    ),
    include_prompt: bool = typer.Option(
        False,
        "--include-prompt/--metadata-only",
        help="Include the composed OfficeX prompt in the provider report.",
    ),
    catalog_path: Path = typer.Option(
        DEFAULT_PROVIDER_CATALOG_MANIFEST,
        "--catalog-path",
        help="Path to the OfficeX provider catalog YAML.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .provider_runtime import build_provider_prompt_binding

    try:
        binding = build_provider_prompt_binding(
            provider,
            role=role,
            model_id=model,
            include_cognition=include_cognition,
            catalog_path=catalog_path.expanduser().resolve(),
        )
    except ValueError as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc

    payload = binding.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_provider_binding(payload, include_prompt=include_prompt))


@officex_provider_app.command("build-request")
def officex_provider_build_request(
    provider: str = typer.Option(
        ...,
        "--provider",
        help="OfficeX provider id.",
    ),
    role: str = typer.Option(
        "orchestrator",
        "--role",
        help="OfficeX role prompt id.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        help="Optional explicit provider model id.",
    ),
    task_packet: Optional[Path] = typer.Option(
        None,
        "--task-packet",
        help="Explicit path to a task_packet.json file.",
    ),
    run_id: Optional[str] = typer.Option(
        None,
        "--run-id",
        help="Sandbox run id used to resolve runtime/task_packet.json.",
    ),
    sandbox_root: Path = typer.Option(
        SANDBOXES_DIR,
        "--sandbox-root",
        help="Root directory for OfficeX sandboxes.",
    ),
    config_field: list[str] = typer.Option(
        None,
        "--config-field",
        help="Repeatable provider config field assignment in `name=value` form.",
    ),
    response_contract_kind: str = typer.Option(
        "plan_object",
        "--response-contract-kind",
        help="Expected provider response contract kind.",
    ),
    include_cognition: bool = typer.Option(
        True,
        "--include-cognition/--role-only",
        help="Include the OfficeX cognition layer before the role prompt.",
    ),
    catalog_path: Path = typer.Option(
        DEFAULT_PROVIDER_CATALOG_MANIFEST,
        "--catalog-path",
        help="Path to the OfficeX provider catalog YAML.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .provider_runtime import build_provider_request_envelope

    try:
        envelope = build_provider_request_envelope(
            provider,
            role=role,
            model_id=model,
            include_cognition=include_cognition,
            task_packet_path=task_packet.expanduser().resolve() if task_packet is not None else None,
            run_id=run_id,
            sandbox_root=sandbox_root.expanduser().resolve(),
            config_field_assignments=config_field,
            response_contract_kind=response_contract_kind,
            catalog_path=catalog_path.expanduser().resolve(),
        )
    except (ValueError, FileNotFoundError) as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc

    payload = envelope.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_provider_request(payload))


@officex_agent_app.command("list")
def officex_agent_list(
    catalog_path: Path = typer.Option(
        DEFAULT_AGENT_CATALOG_MANIFEST,
        "--catalog-path",
        help="Path to the OfficeX agent catalog YAML.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .agent_runtime import load_agent_catalog_manifest

    catalog = load_agent_catalog_manifest(catalog_path.expanduser().resolve())
    payload = catalog.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_agent_list(payload))


@officex_agent_app.command("show")
def officex_agent_show(
    agent: str = typer.Option(
        ...,
        "--agent",
        help="OfficeX agent id.",
    ),
    catalog_path: Path = typer.Option(
        DEFAULT_AGENT_CATALOG_MANIFEST,
        "--catalog-path",
        help="Path to the OfficeX agent catalog YAML.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .agent_runtime import get_agent_entry

    try:
        entry = get_agent_entry(agent, catalog_path=catalog_path.expanduser().resolve())
    except ValueError as exc:
        console.print(str(exc))
        raise typer.Exit(code=1) from exc

    payload = entry.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_agent_show(payload))


@officex_trace_app.command("checkpoint")
def officex_trace_checkpoint(
    title: str = typer.Option(
        ...,
        "--title",
        help="Checkpoint title.",
    ),
    summary_line: list[str] = typer.Option(
        None,
        "--summary-line",
        help="Repeat to append summary bullet lines.",
    ),
    verification_line: list[str] = typer.Option(
        None,
        "--verification-line",
        help="Repeat to append verification bullet lines.",
    ),
    follow_up_line: list[str] = typer.Option(
        None,
        "--follow-up-line",
        help="Repeat to append follow-up bullet lines.",
    ),
    trace_dir: Path = typer.Option(
        TRACE_DIR,
        "--trace-dir",
        help="Trace directory for the new checkpoint.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .trace_runtime import create_trace_checkpoint

    report = create_trace_checkpoint(
        title=title,
        summary_lines=summary_line or [],
        verification_lines=verification_line or [],
        follow_up_lines=follow_up_line or [],
        trace_dir=trace_dir.expanduser().resolve(),
    )
    payload = report.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(render_officex_trace_checkpoint(payload))


@officex_app.command("generate")
def officex_generate(
    prompt: str = typer.Option(
        ...,
        "--prompt",
        help="Document generation prompt describing what to create.",
    ),
    provider: str = typer.Option(
        "compatible_local",
        "--provider",
        help="OfficeX provider id.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        help="Provider model id.",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        help="Output directory for generated artifacts.",
    ),
    no_visual: bool = typer.Option(
        False,
        "--no-visual",
        help="Skip visual audit step.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .generate_runtime import run_generate

    report = run_generate(
        prompt=prompt,
        provider_id=provider,
        model_id=model,
        output_dir=output_dir.expanduser().resolve() if output_dir else None,
        include_visual_audit=not no_visual,
    )

    if as_json:
        console.print_json(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        if report.status not in {"success", "validation_warnings"}:
            raise typer.Exit(code=1)
        return

    if report.status in {"ai_failed", "build_failed"}:
        console.print(f"[red]Generate failed: {report.error_message}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[green]Generated:[/green] {report.output_docx}")
    console.print(f"Model: {report.ai_model} | Tokens: {report.ai_tokens}")
    console.print(f"Validation: {report.validation_errors} error(s), {report.validation_warnings} warning(s)")
    if report.page_count:
        console.print(f"Visual: {report.page_count} page(s), {report.visual_findings} finding(s)")


@officex_audit_app.command("visual")
def officex_audit_visual(
    candidate_docx: Path = typer.Option(
        ...,
        "--candidate-docx",
        help="Candidate docx to render and visually audit.",
    ),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        help="Directory for rendered PNG pages and audit report.",
    ),
    dpi: int = typer.Option(
        150,
        "--dpi",
        help="Rendering resolution in DPI.",
    ),
    as_json: bool = typer.Option(
        False,
        "--as-json",
        help="Emit machine-readable JSON instead of a formatted summary.",
    ),
) -> None:
    from .visual_audit import render_docx_to_png
    from .visual_audit_checks import run_visual_checks

    render_report = render_docx_to_png(
        candidate_docx.expanduser().resolve(),
        output_dir.expanduser().resolve(),
        dpi=dpi,
    )

    if render_report.status == "renderer_unavailable":
        console.print("LibreOffice (soffice) not found. Visual audit requires a renderer.")
        raise typer.Exit(code=2)

    if render_report.status == "render_failed":
        console.print("Rendering failed. Check logs for details.")
        raise typer.Exit(code=1)

    visual_findings = run_visual_checks(render_report.png_paths)
    render_report.findings = visual_findings

    payload = render_report.model_dump(mode="json")
    if as_json:
        console.print_json(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    lines = [
        f"Rendered {render_report.page_count} page(s) from {candidate_docx}",
        f"Renderer: {render_report.renderer_name} {render_report.renderer_version}",
        f"Output: {render_report.output_dir}",
    ]
    if visual_findings:
        lines.append(f"Visual findings: {len(visual_findings)}")
        for finding in visual_findings:
            lines.append(f"  [{finding.severity.upper()}] page {finding.page}: {finding.message}")
    else:
        lines.append("Visual audit: clean")
    console.print("\n".join(lines))

    if any(f.severity == "error" for f in visual_findings):
        raise typer.Exit(code=1)


@app.command("check-fonts")
def check_fonts(
    docx: Optional[Path] = typer.Option(
        None,
        "--docx",
        help="Optional explicit target docx. Defaults to manifests/baseline.yml",
    ),
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
    output_dir: Path = typer.Option(
        FONT_AUDIT_DIR,
        "--output-dir",
        help="Directory for generated font audit reports.",
    ),
    expected_font: str = typer.Option(
        "Times New Roman",
        "--expected-font",
        help="Expected explicit run font for the audit.",
    ),
) -> None:
    from .font_audit import render_font_audit_markdown, scan_docx_fonts

    target_docx, _, _ = resolve_target_context(docx, baseline_manifest)
    ensure_dir(output_dir)

    report = scan_docx_fonts(target_docx, expected_font=expected_font)
    write_json(output_dir / "font_audit.json", report.model_dump(mode="json"))
    write_markdown(output_dir / "font_audit.md", render_font_audit_markdown(report))
    write_markdown(
        output_dir / "font_audit_summary.md",
        render_font_audit_summary(report.model_dump(mode="json")),
    )

    console.print(
        f"Scanned fonts in {target_docx}; explicit other-font runs: {report.explicit_other_font_runs}."
    )


@app.command("check-outline")
def check_outline(
    docx: Optional[Path] = typer.Option(
        None,
        "--docx",
        help="Optional explicit target docx. Defaults to manifests/baseline.yml",
    ),
    baseline_manifest: Path = typer.Option(
        DEFAULT_BASELINE_MANIFEST,
        "--baseline-manifest",
        help="Path to the baseline manifest YAML.",
    ),
    output_dir: Path = typer.Option(
        OUTLINE_AUDIT_DIR,
        "--output-dir",
        help="Directory for generated outline audit reports.",
    ),
) -> None:
    from .outline_audit import render_outline_audit_markdown, scan_docx_outline

    target_docx, _, _ = resolve_target_context(docx, baseline_manifest)
    ensure_dir(output_dir)

    report = scan_docx_outline(target_docx)
    write_json(output_dir / "outline_audit.json", report.model_dump(mode="json"))
    write_markdown(output_dir / "outline_audit.md", render_outline_audit_markdown(report))
    write_markdown(
        output_dir / "outline_audit_summary.md",
        render_outline_audit_summary(report.model_dump(mode="json")),
    )

    console.print(f"Scanned outline in {target_docx}")
    console.print(
        f"Headings: {report.heading_count}; appendix headings: {report.appendix_heading_count}."
    )


@app.command("check-candidate")
def check_candidate(
    docx: Path = typer.Option(
        ...,
        "--docx",
        help="Candidate output docx to audit.",
    ),
    source: Path = typer.Option(
        DEFAULT_BUILD_SOURCE,
        "--source",
        help="Structured build source used to produce the candidate.",
    ),
    write_contract: Path = typer.Option(
        DEFAULT_WRITE_CONTRACT_MANIFEST,
        "--write-contract",
        help="Write contract YAML used to produce the candidate.",
    ),
    output_dir: Path = typer.Option(
        CANDIDATE_AUDIT_DIR,
        "--output-dir",
        help="Directory for generated candidate audit reports.",
    ),
) -> None:
    from .candidate_audit import build_candidate_audit, render_candidate_audit_markdown

    target_docx = docx.expanduser().resolve()
    ensure_dir(output_dir)

    report = build_candidate_audit(
        target_docx,
        build_source_path=source,
        write_contract_path=write_contract,
    )
    write_json(output_dir / "candidate_audit.json", report.model_dump(mode="json"))
    write_markdown(output_dir / "candidate_audit.md", render_candidate_audit_markdown(report))
    write_markdown(
        output_dir / "candidate_audit_summary.md",
        render_candidate_audit_summary(report.model_dump(mode="json")),
    )

    error_count = sum(1 for finding in report.findings if finding.severity == "error")
    warning_count = sum(1 for finding in report.findings if finding.severity == "warning")
    console.print(
        f"Audited candidate {target_docx}; {error_count} error(s), {warning_count} warning(s)."
    )


@app.command("assemble-sections")
def assemble_sections(
    output_source: Path = typer.Option(
        DEFAULT_SECTION_BUILD_SOURCE,
        "--output-source",
        help="Generated build-source YAML path.",
    ),
    snippets_manifest: Path = typer.Option(
        DEFAULT_SNIPPETS_MANIFEST,
        "--snippets-manifest",
        help="Optional snippets manifest YAML path. Defaults to manifests/snippets.yml.",
    ),
) -> None:
    from .manifest_loader import load_figures_manifest, load_sections_manifest, load_snippets_manifest
    from .section_assembler import assemble_sections_manifest, write_build_source_yaml

    sections_manifest = load_sections_manifest()
    figures_manifest = load_figures_manifest()
    snippets = load_snippets_manifest(snippets_manifest.expanduser().resolve())
    build_source = assemble_sections_manifest(
        sections_manifest,
        figures_manifest=figures_manifest,
        snippets_manifest=snippets,
    )
    resolved_output = output_source.expanduser().resolve()
    ensure_dir(resolved_output.parent)
    write_build_source_yaml(build_source, resolved_output)
    summary_json_path, summary_markdown_path = section_summary_paths(resolved_output)
    build_source_payload = build_source.model_dump(mode="json")
    write_json(summary_json_path, build_source_payload)
    write_markdown(
        summary_markdown_path,
        render_section_assembly_summary(build_source_payload, output_path=resolved_output),
    )
    if is_within_directory(resolved_output, BUILD_SOURCES_DIR):
        ensure_dir(BUILD_SOURCES_DIR)
        write_json(BUILD_SOURCES_DIR / "assembled_sections_summary.json", build_source_payload)
        write_markdown(
            BUILD_SOURCES_DIR / "assembled_sections_summary.md",
            render_section_assembly_summary(build_source_payload, output_path=resolved_output),
        )

    console.print(f"Assembled section-managed build source at {resolved_output}")


@app.command("check-snippets")
def check_snippets(
    snippets_manifest: Path = typer.Option(
        DEFAULT_SNIPPETS_MANIFEST,
        "--snippets-manifest",
        help="Path to the snippets manifest YAML.",
    ),
    output_dir: Path = typer.Option(
        SNIPPET_AUDIT_DIR,
        "--output-dir",
        help="Directory for generated snippet audit reports.",
    ),
) -> None:
    from .snippet_audit import build_snippet_audit, render_snippet_audit_markdown

    resolved_manifest = snippets_manifest.expanduser().resolve()
    ensure_dir(output_dir)

    report = build_snippet_audit(resolved_manifest)
    write_json(output_dir / "snippet_audit.json", report.model_dump(mode="json"))
    write_markdown(output_dir / "snippet_audit.md", render_snippet_audit_markdown(report))
    write_markdown(
        output_dir / "snippet_audit_summary.md",
        render_snippet_audit_summary(report.model_dump(mode="json")),
    )

    error_count = sum(1 for finding in report.findings if finding.severity == "error")
    warning_count = sum(1 for finding in report.findings if finding.severity == "warning")
    console.print(
        f"Audited snippets from {resolved_manifest}; {error_count} error(s), {warning_count} warning(s)."
    )


@app.command("run-section-pipeline")
def run_section_pipeline_command(
    output_dir: Path = typer.Option(
        SECTION_PIPELINE_DIR,
        "--output-dir",
        help="Directory for sequential section build, candidate audit, and validation outputs.",
    ),
) -> None:
    from .section_pipeline import run_section_pipeline

    resolved_output_dir = output_dir.expanduser().resolve()
    ensure_dir(resolved_output_dir)

    report = run_section_pipeline(pipeline_dir=resolved_output_dir)
    write_json(
        resolved_output_dir / "section_pipeline_summary.json",
        report.model_dump(mode="json"),
    )
    write_markdown(
        resolved_output_dir / "section_pipeline_summary.md",
        render_section_pipeline_summary(report.model_dump(mode="json")),
    )

    console.print(
        "Ran section pipeline sequentially: "
        f"candidate {report.candidate_error_count} error(s), {report.candidate_warning_count} warning(s); "
        f"validation {report.validation_error_count} error(s), {report.validation_warning_count} warning(s)."
    )


@app.command("publish-run")
def publish_run_command(
    run_dir: Path = typer.Option(
        SECTION_PIPELINE_DIR,
        "--run-dir",
        help="Run directory to publish.",
    ),
    output_dir: Path = typer.Option(
        PUBLISHED_DIR,
        "--output-dir",
        help="Directory for canonical published metadata.",
    ),
) -> None:
    from .publication import publish_run

    resolved_run_dir = run_dir.expanduser().resolve()
    resolved_output_dir = output_dir.expanduser().resolve()
    ensure_dir(resolved_output_dir)

    manifest = publish_run(run_dir=resolved_run_dir, published_dir=resolved_output_dir)
    write_markdown(
        resolved_output_dir / "current_summary.md",
        render_published_run_summary(manifest.model_dump(mode="json")),
    )

    console.print(
        f"Published run {manifest.published_id} from {resolved_run_dir} into {resolved_output_dir}."
    )


@app.command("index-trace")
def index_trace(
    trace_dir: Path = typer.Option(
        TRACE_DIR,
        "--trace-dir",
        help="Trace directory to catalog.",
    ),
) -> None:
    from .trace_indexer import build_trace_index_report, write_trace_index

    resolved_trace_dir = trace_dir.expanduser().resolve()
    report = build_trace_index_report(resolved_trace_dir)
    write_trace_index(report, trace_dir=resolved_trace_dir)
    write_markdown(
        resolved_trace_dir / "checkpoint_catalog_summary.md",
        render_trace_catalog_summary(report.model_dump(mode="json")),
    )

    console.print(
        f"Indexed trace {resolved_trace_dir}; {report.checkpoint_count} checkpoint(s), latest {report.latest_checkpoint_id}."
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
