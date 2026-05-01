from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
import sys

from .paths import PACKAGE_DIR


@dataclass(frozen=True)
class CoreModuleSpec:
    file_name: str
    import_name: str
    purpose: str


@dataclass(frozen=True)
class PackageIntegrityIssue:
    code: str
    message: str


MIN_SUPPORTED_PYTHON = (3, 11)


CORE_MODULES: tuple[CoreModuleSpec, ...] = (
    CoreModuleSpec("__init__.py", "tools.report_scaffold_v3", "package bootstrap"),
    CoreModuleSpec("agent_runtime.py", "tools.report_scaffold_v3.agent_runtime", "OfficeX agent runtime"),
    CoreModuleSpec("cli.py", "tools.report_scaffold_v3.cli", "CLI entrypoint"),
    CoreModuleSpec("candidate_audit.py", "tools.report_scaffold_v3.candidate_audit", "candidate-specific audit module"),
    CoreModuleSpec("docx_inspector.py", "tools.report_scaffold_v3.docx_inspector", "docx inventory import"),
    CoreModuleSpec("font_audit.py", "tools.report_scaffold_v3.font_audit", "font audit module"),
    CoreModuleSpec("manifest_loader.py", "tools.report_scaffold_v3.manifest_loader", "manifest loading"),
    CoreModuleSpec("models.py", "tools.report_scaffold_v3.models", "shared models"),
    CoreModuleSpec("ooxml_inspector.py", "tools.report_scaffold_v3.ooxml_inspector", "OOXML inspection"),
    CoreModuleSpec("ooxml_styles.py", "tools.report_scaffold_v3.ooxml_styles", "OOXML style extraction"),
    CoreModuleSpec("outline_audit.py", "tools.report_scaffold_v3.outline_audit", "outline audit module"),
    CoreModuleSpec("officex_runtime.py", "tools.report_scaffold_v3.officex_runtime", "OfficeX runtime services"),
    CoreModuleSpec("doctor_runtime.py", "tools.report_scaffold_v3.doctor_runtime", "OfficeX environment doctor"),
    CoreModuleSpec("officex_exec/__init__.py", "tools.report_scaffold_v3.officex_exec", "OfficeX execution core bootstrap"),
    CoreModuleSpec("officex_exec/common.py", "tools.report_scaffold_v3.officex_exec.common", "OfficeX execution core shared utilities"),
    CoreModuleSpec("officex_exec/models.py", "tools.report_scaffold_v3.officex_exec.models", "OfficeX execution core models"),
    CoreModuleSpec("officex_exec/anchor_extractor.py", "tools.report_scaffold_v3.officex_exec.anchor_extractor", "OfficeX live anchor extraction"),
    CoreModuleSpec("officex_exec/executor.py", "tools.report_scaffold_v3.officex_exec.executor", "OfficeX deterministic executor"),
    CoreModuleSpec("patch_bridge_runtime.py", "tools.report_scaffold_v3.patch_bridge_runtime", "OfficeX patch bridge runtime"),
    CoreModuleSpec("package_contract.py", "tools.report_scaffold_v3.package_contract", "package contract"),
    CoreModuleSpec("paths.py", "tools.report_scaffold_v3.paths", "path registry"),
    CoreModuleSpec("product_common.py", "tools.report_scaffold_v3.product_common", "OfficeX product runtime helpers"),
    CoreModuleSpec("product_entry.py", "tools.report_scaffold_v3.product_entry", "OfficeX product entrypoint"),
    CoreModuleSpec("product_models.py", "tools.report_scaffold_v3.product_models", "OfficeX product-facing models"),
    CoreModuleSpec("prompt_runtime.py", "tools.report_scaffold_v3.prompt_runtime", "OfficeX prompt runtime"),
    CoreModuleSpec("provider_runtime.py", "tools.report_scaffold_v3.provider_runtime", "OfficeX provider runtime"),
    CoreModuleSpec("publication.py", "tools.report_scaffold_v3.publication", "canonical publication module"),
    CoreModuleSpec("render_boundary_runtime.py", "tools.report_scaffold_v3.render_boundary_runtime", "OfficeX renderer boundary runtime"),
    CoreModuleSpec("review_runtime.py", "tools.report_scaffold_v3.review_runtime", "OfficeX review prep runtime"),
    CoreModuleSpec("runtime_common.py", "tools.report_scaffold_v3.runtime_common", "OfficeX runtime shared helpers"),
    CoreModuleSpec("section_assembler.py", "tools.report_scaffold_v3.section_assembler", "section assembly module"),
    CoreModuleSpec("section_pipeline.py", "tools.report_scaffold_v3.section_pipeline", "sequential section pipeline"),
    CoreModuleSpec("snippet_audit.py", "tools.report_scaffold_v3.snippet_audit", "snippet audit module"),
    CoreModuleSpec("snippet_compiler.py", "tools.report_scaffold_v3.snippet_compiler", "snippet compiler"),
    CoreModuleSpec("task_runtime.py", "tools.report_scaffold_v3.task_runtime", "OfficeX task runtime"),
    CoreModuleSpec("trace_indexer.py", "tools.report_scaffold_v3.trace_indexer", "trace indexing module"),
    CoreModuleSpec("trace_runtime.py", "tools.report_scaffold_v3.trace_runtime", "OfficeX trace runtime"),
    CoreModuleSpec("cli_render.py", "tools.report_scaffold_v3.cli_render", "CLI rendering helpers"),
    CoreModuleSpec("validation/__init__.py", "tools.report_scaffold_v3.validation", "validation engine"),
    CoreModuleSpec("validation/common.py", "tools.report_scaffold_v3.validation.common", "validation shared utilities"),
    CoreModuleSpec("validation/page_setup.py", "tools.report_scaffold_v3.validation.page_setup", "page setup validation"),
    CoreModuleSpec("validation/style_contract.py", "tools.report_scaffold_v3.validation.style_contract", "style contract validation"),
    CoreModuleSpec("validation/image_fit.py", "tools.report_scaffold_v3.validation.image_fit", "image fit validation"),
    CoreModuleSpec("validation/override_detection.py", "tools.report_scaffold_v3.validation.override_detection", "override detection"),
    CoreModuleSpec("visual_audit.py", "tools.report_scaffold_v3.visual_audit", "visual audit renderer"),
    CoreModuleSpec("visual_audit_checks.py", "tools.report_scaffold_v3.visual_audit_checks", "visual audit deterministic checks"),
    CoreModuleSpec("workspace_runtime.py", "tools.report_scaffold_v3.workspace_runtime", "OfficeX workspace runtime"),
    CoreModuleSpec("writer.py", "tools.report_scaffold_v3.writer", "rule-driven docx writer"),
)


def collect_package_integrity_issues(
    *,
    package_root: Path | None = None,
    check_imports: bool = True,
) -> list[PackageIntegrityIssue]:
    root = package_root or PACKAGE_DIR
    issues: list[PackageIntegrityIssue] = []

    if sys.version_info < MIN_SUPPORTED_PYTHON:
        issues.append(
            PackageIntegrityIssue(
                code="python-version-too-old",
                message=(
                    "OfficeX requires Python "
                    f"{MIN_SUPPORTED_PYTHON[0]}.{MIN_SUPPORTED_PYTHON[1]}+ but the active "
                    "runtime is "
                    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}."
                ),
            )
        )

    for spec in CORE_MODULES:
        if not (root / spec.file_name).exists():
            issues.append(
                PackageIntegrityIssue(
                    code="missing-core-module-file",
                    message=(
                        f"Required core module `{spec.file_name}` is missing "
                        f"({spec.purpose})."
                    ),
                )
            )

    if check_imports:
        for spec in CORE_MODULES:
            try:
                import_module(spec.import_name)
            except Exception as exc:  # pragma: no cover - defensive boundary
                issues.append(
                    PackageIntegrityIssue(
                        code="core-module-import-failed",
                        message=(
                            f"Required core module `{spec.import_name}` failed to import "
                            f"({spec.purpose}): {exc}"
                        ),
                    )
                )

    deduped: list[PackageIntegrityIssue] = []
    seen = set()
    for issue in issues:
        key = (issue.code, issue.message)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(issue)
    return deduped


def format_package_integrity_report(issues: list[PackageIntegrityIssue]) -> str:
    lines = ["OfficeX runtime package integrity check failed:"]
    for issue in issues:
        lines.append(f"- [{issue.code}] {issue.message}")
    return "\n".join(lines)
