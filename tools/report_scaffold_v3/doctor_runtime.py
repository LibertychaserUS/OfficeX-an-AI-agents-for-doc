from __future__ import annotations

import platform
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from .manifest_loader import load_provider_catalog
from .officex_runtime import run_docx_mvp
from .package_contract import collect_package_integrity_issues
from .paths import (
    DEFAULT_BASELINE_MANIFEST,
    DEFAULT_OFFICEX_DESKTOP_SHELL_DIR,
    DEFAULT_PROVIDER_CATALOG_MANIFEST,
    DEFAULT_WRITE_CONTRACT_MANIFEST,
    DEFAULT_BUILD_SOURCE,
)
from .product_common import (
    default_machine_settings_dir,
    detect_bun_binary,
    detect_provider_config_state,
    detect_word_app,
    find_packaged_app_bundle,
    resolve_desktop_shell_dir,
)
from .product_models import OfficeXCheckStatus, OfficeXDoctorCheck, OfficeXDoctorReport
from .runtime_common import (
    local_now_iso,
    sanitize_runtime_identifier,
    write_runtime_json,
    write_runtime_markdown,
)


def _make_report_id(prefix: str) -> str:
    return sanitize_runtime_identifier(
        f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}",
        fallback=prefix,
    )


def _doctor_report_root(settings_dir: Path) -> Path:
    return settings_dir / "reports" / "doctor"


def doctor_latest_report_json_path(settings_dir: Path) -> Path:
    return _doctor_report_root(settings_dir) / "latest.json"


def doctor_latest_report_markdown_path(settings_dir: Path) -> Path:
    return _doctor_report_root(settings_dir) / "latest.md"


def _check_writable_directory(path: Path) -> tuple[OfficeXCheckStatus, list[str]]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".officex-write-check"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return "pass", [f"`{path}` is writable."]
    except Exception as exc:  # pragma: no cover - defensive boundary
        return "fail", [f"`{path}` is not writable: {exc}"]


def run_doctor_smoke_check(sandbox_root: Path) -> tuple[OfficeXCheckStatus, str]:
    sandbox_root.mkdir(parents=True, exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix="officex-doctor-", dir=str(sandbox_root)))
    try:
        report = run_docx_mvp(
            run_id="doctor-smoke",
            sandbox_root=temp_root,
            source_path=DEFAULT_BUILD_SOURCE,
            baseline_manifest_path=DEFAULT_BASELINE_MANIFEST,
            write_contract_path=DEFAULT_WRITE_CONTRACT_MANIFEST,
            approval_mode="ask_every_conflict",
        )
        if report.candidate_docx.exists() and report.validation_error_count == 0:
            return "pass", "Smoke run completed."
        return "fail", "Smoke run did not complete cleanly."
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def build_doctor_report(
    *,
    workspace_root: Path,
    sandbox_root: Path,
    desktop_shell_dir: Path | None = None,
) -> OfficeXDoctorReport:
    resolved_workspace = workspace_root.expanduser().resolve()
    resolved_sandbox = sandbox_root.expanduser().resolve()
    resolved_desktop_dir = resolve_desktop_shell_dir(desktop_shell_dir)
    settings_dir = default_machine_settings_dir()
    generated_at = local_now_iso()
    checks: list[OfficeXDoctorCheck] = []

    package_issues = collect_package_integrity_issues()
    package_status: OfficeXCheckStatus = "pass" if not package_issues else "fail"
    checks.append(
        OfficeXDoctorCheck(
            check_id="python_runtime",
            title="Python runtime and package integrity",
            status=package_status,
            summary="OfficeX Python runtime is healthy."
            if package_status == "pass"
            else "OfficeX Python runtime or imports are not healthy.",
            detail_lines=[issue.message for issue in package_issues],
            remediation=["Run `officex doctor` after repairing the Python environment."]
            if package_status == "fail"
            else [],
        )
    )

    bun_binary = detect_bun_binary()
    checks.append(
        OfficeXDoctorCheck(
            check_id="bun_runtime",
            title="Bun runtime",
            status="pass" if bun_binary else "warning",
            summary=f"Bun detected at `{bun_binary}`."
            if bun_binary
            else "Bun is not installed or not on PATH.",
            remediation=["Install Bun for the Electron desktop shell."]
            if bun_binary is None
            else [],
        )
    )

    desktop_package_json = resolved_desktop_dir / "package.json"
    desktop_node_modules = resolved_desktop_dir / "node_modules"
    packaged_app_bundle = find_packaged_app_bundle(resolved_desktop_dir)
    if (
        resolved_desktop_dir.exists()
        and desktop_package_json.exists()
        and (desktop_node_modules.exists() or packaged_app_bundle is not None)
    ):
        desktop_status: OfficeXCheckStatus = "pass"
        desktop_summary = f"Desktop shell detected at `{resolved_desktop_dir}`."
        desktop_remediation: list[str] = []
    elif resolved_desktop_dir.exists() and desktop_package_json.exists():
        desktop_status = "warning"
        desktop_summary = (
            f"Desktop shell source is present at `{resolved_desktop_dir}`, "
            "but desktop dependencies are not installed yet."
        )
        desktop_remediation = ["Run `cd desktop && bun install` before launching OfficeX."]
    elif resolved_desktop_dir.exists():
        desktop_status = "warning"
        desktop_summary = f"Desktop shell directory exists at `{resolved_desktop_dir}`, but package.json is missing."
        desktop_remediation = ["Scaffold or repair the OfficeX desktop shell."]
    else:
        desktop_status = "skipped"
        desktop_summary = f"Desktop shell has not been scaffolded yet at `{resolved_desktop_dir}`."
        desktop_remediation = []
    checks.append(
        OfficeXDoctorCheck(
            check_id="desktop_shell",
            title="Electron desktop shell",
            status=desktop_status,
            summary=desktop_summary,
            remediation=desktop_remediation,
        )
    )

    word_app = detect_word_app()
    checks.append(
        OfficeXDoctorCheck(
            check_id="word_app",
            title="Microsoft Word",
            status="pass" if word_app else "fail",
            summary=f"Microsoft Word detected at `{word_app}`."
            if word_app
            else "Microsoft Word is not installed or not detectable.",
            remediation=["Install Microsoft Word or configure the detection path."]
            if word_app is None
            else [],
        )
    )

    workspace_status, workspace_details = _check_writable_directory(resolved_workspace)
    checks.append(
        OfficeXDoctorCheck(
            check_id="workspace_root",
            title="Workspace root",
            status=workspace_status,
            summary="Workspace root is writable."
            if workspace_status == "pass"
            else "Workspace root is not writable.",
            detail_lines=workspace_details,
        )
    )

    sandbox_status, sandbox_details = _check_writable_directory(resolved_sandbox)
    checks.append(
        OfficeXDoctorCheck(
            check_id="sandbox_root",
            title="Sandbox root",
            status=sandbox_status,
            summary="Sandbox root is writable."
            if sandbox_status == "pass"
            else "Sandbox root is not writable.",
            detail_lines=sandbox_details,
        )
    )

    try:
        catalog = load_provider_catalog(DEFAULT_PROVIDER_CATALOG_MANIFEST)
        provider_catalog_status: OfficeXCheckStatus = "pass"
        provider_catalog_summary = (
            f"Provider catalog loaded with {len(catalog.providers)} provider(s)."
        )
    except Exception as exc:  # pragma: no cover - defensive boundary
        provider_catalog_status = "fail"
        provider_catalog_summary = f"Provider catalog could not be read: {exc}"
    checks.append(
        OfficeXDoctorCheck(
            check_id="provider_catalog",
            title="Provider catalog",
            status=provider_catalog_status,
            summary=provider_catalog_summary,
        )
    )

    provider_state = detect_provider_config_state()
    checks.append(
        OfficeXDoctorCheck(
            check_id="provider_config",
            title="Provider configuration",
            status="pass" if provider_state["configured"] else "warning",
            summary="Provider configuration detected."
            if provider_state["configured"]
            else "No provider credentials were detected in the current environment.",
            detail_lines=[
                f"Configured sources: {', '.join(provider_state['sources'])}"
                if provider_state["sources"]
                else "Configured sources: none"
            ],
            remediation=["Set provider credentials before running live model requests."]
            if not provider_state["configured"]
            else [],
        )
    )

    try:
        smoke_status, smoke_message = run_doctor_smoke_check(resolved_sandbox)
    except Exception as exc:  # pragma: no cover - defensive boundary
        smoke_status = "fail"
        smoke_message = f"Smoke run raised an exception: {exc}"
    checks.append(
        OfficeXDoctorCheck(
            check_id="smoke_run",
            title="Runtime smoke run",
            status=smoke_status,
            summary=smoke_message,
            remediation=["Investigate runtime smoke failures before using the app."]
            if smoke_status == "fail"
            else [],
        )
    )

    if any(check.status == "fail" for check in checks):
        overall_status: OfficeXCheckStatus = "fail"
        recommended_next_action = "Fix failed checks before launching OfficeX."
    elif any(check.status == "warning" for check in checks):
        overall_status = "warning"
        recommended_next_action = "OfficeX can start, but some setup is incomplete."
    else:
        overall_status = "pass"
        recommended_next_action = "This Mac is ready for the first OfficeX app MVP run."

    return OfficeXDoctorReport(
        report_id=_make_report_id("officex-doctor"),
        generated_at=generated_at,
        overall_status=overall_status,
        platform=platform.system().lower(),
        workspace_root=resolved_workspace,
        sandbox_root=resolved_sandbox,
        machine_settings_dir=settings_dir,
        desktop_shell_dir=resolved_desktop_dir,
        recommended_next_action=recommended_next_action,
        checks=checks,
    )


def persist_doctor_report(report: OfficeXDoctorReport) -> OfficeXDoctorReport:
    report_root = _doctor_report_root(report.machine_settings_dir)
    archive_dir = report_root / report.report_id
    archive_dir.mkdir(parents=True, exist_ok=True)

    json_path = archive_dir / "doctor_report.json"
    markdown_path = archive_dir / "doctor_report.md"
    persisted_report = report.model_copy(
        update={
            "report_json_path": json_path,
            "report_markdown_path": markdown_path,
        }
    )
    write_runtime_json(json_path, persisted_report.model_dump(mode="json"))
    write_runtime_markdown(markdown_path, render_doctor_report_markdown(persisted_report))
    shutil.copyfile(json_path, doctor_latest_report_json_path(report.machine_settings_dir))
    shutil.copyfile(markdown_path, doctor_latest_report_markdown_path(report.machine_settings_dir))
    return persisted_report


def render_doctor_report_markdown(report: OfficeXDoctorReport) -> str:
    lines = [
        "# OfficeX Doctor Report",
        "",
        f"- Report id: `{report.report_id}`",
        f"- Generated at: `{report.generated_at}`",
        f"- Overall status: `{report.overall_status}`",
        f"- Platform: `{report.platform}`",
        f"- Workspace root: `{report.workspace_root}`",
        f"- Sandbox root: `{report.sandbox_root}`",
        f"- Machine settings dir: `{report.machine_settings_dir}`",
        f"- Desktop shell dir: `{report.desktop_shell_dir}`",
        f"- Next action: {report.recommended_next_action}",
        "",
    ]
    for check in report.checks:
        lines.extend(
            [
                f"## {check.title}",
                "",
                f"- Check id: `{check.check_id}`",
                f"- Status: `{check.status}`",
                f"- Summary: {check.summary}",
            ]
        )
        if check.detail_lines:
            lines.append("- Details:")
            lines.extend([f"  - {line}" for line in check.detail_lines])
        if check.remediation:
            lines.append("- Remediation:")
            lines.extend([f"  - {line}" for line in check.remediation])
        lines.append("")
    return "\n".join(lines)
