from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from tools.report_scaffold_v3.render_boundary_runtime import (
    build_render_boundary_report,
    persist_render_boundary_report,
)


def test_build_render_boundary_report_flags_missing_word_renderer(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "tools.report_scaffold_v3.render_boundary_runtime.detect_word_app",
        lambda: None,
    )

    report = build_render_boundary_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
    )

    assert report.renderer_profile.detected is False
    assert report.overall_status == "fail"
    assert any("not detected" in note.lower() for note in report.residual_risk_notes)


def test_build_render_boundary_report_includes_expected_length_profiles(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "tools.report_scaffold_v3.render_boundary_runtime.detect_word_app",
        lambda: Path("/Applications/Microsoft Word.app"),
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.render_boundary_runtime.collect_length_profile_results",
        lambda *, build_sources_dir, benchmark_root: [
            {
                "scenario_id": "short-plain",
                "document_length": "short",
                "structure_profile": "plain_text",
                "operation_profile": "replace_text",
                "status": "pass",
                "localization_confidence": 0.95,
                "patch_applicability_confidence": 0.95,
                "requires_human_review": False,
                "notes": ["Stable in current environment."],
            },
            {
                "scenario_id": "ultra-long-headings",
                "document_length": "ultra_long",
                "structure_profile": "heading_numbering",
                "operation_profile": "restyle",
                "status": "warning",
                "localization_confidence": 0.8,
                "patch_applicability_confidence": 0.75,
                "requires_human_review": True,
                "notes": ["Manual review still advised for long documents."],
            },
        ],
    )

    report = build_render_boundary_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
    )

    assert report.renderer_profile.detected is True
    assert [scenario.document_length for scenario in report.scenarios] == ["short", "ultra_long"]
    assert report.capability_matrix["replace_text"]["short"] == "pass"
    assert report.capability_matrix["restyle"]["ultra_long"] == "warning"


def test_build_render_boundary_report_can_be_rerun_with_same_roots(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "tools.report_scaffold_v3.render_boundary_runtime.detect_word_app",
        lambda: Path("/Applications/Microsoft Word.app"),
    )

    def fake_run_docx_mvp(
        *,
        run_id: str,
        sandbox_root: Path,
        source_path: Path,
        baseline_manifest_path: Path,
        write_contract_path: Path,
        approval_mode: str,
    ):
        sandbox_dir = sandbox_root / run_id
        if sandbox_dir.exists():
            raise FileExistsError(f"Sandbox already exists: {sandbox_dir}")
        sandbox_dir.mkdir(parents=True, exist_ok=False)
        return SimpleNamespace(validation_error_count=0, candidate_error_count=0)

    monkeypatch.setattr(
        "tools.report_scaffold_v3.render_boundary_runtime.run_docx_mvp",
        fake_run_docx_mvp,
    )

    first_report = build_render_boundary_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
    )
    second_report = build_render_boundary_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
    )

    assert first_report.overall_status == "warning"
    assert second_report.overall_status == "warning"
    assert len(second_report.scenarios) == 4


def test_persist_render_boundary_report_writes_archive_and_latest_files(
    monkeypatch,
    tmp_path: Path,
):
    settings_dir = tmp_path / "machine-settings"
    monkeypatch.setenv("OFFICEX_SETTINGS_DIR", str(settings_dir))
    monkeypatch.setattr(
        "tools.report_scaffold_v3.render_boundary_runtime.detect_word_app",
        lambda: Path("/Applications/Microsoft Word.app"),
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.render_boundary_runtime.collect_length_profile_results",
        lambda *, build_sources_dir, benchmark_root: [
            {
                "scenario_id": "short-plain",
                "document_length": "short",
                "structure_profile": "plain_text",
                "operation_profile": "replace_text",
                "status": "pass",
                "localization_confidence": 0.95,
                "patch_applicability_confidence": 0.95,
                "requires_human_review": False,
                "notes": ["Stable in current environment."],
            }
        ],
    )

    report = build_render_boundary_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
    )
    persisted = persist_render_boundary_report(report)

    assert persisted.report_json_path is not None
    assert persisted.report_markdown_path is not None
    assert persisted.report_json_path.exists()
    assert persisted.report_markdown_path.exists()
    assert (settings_dir / "reports" / "render-boundary" / "latest.json").exists()
    assert (settings_dir / "reports" / "render-boundary" / "latest.md").exists()
