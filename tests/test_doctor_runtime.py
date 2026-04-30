from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from tools.report_scaffold_v3.doctor_runtime import (
    build_doctor_report,
    persist_doctor_report,
    run_doctor_smoke_check,
)


def test_build_doctor_report_marks_missing_word_as_failure(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_word_app",
        lambda: None,
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_bun_binary",
        lambda: "/opt/homebrew/bin/bun",
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_provider_config_state",
        lambda: {"configured": False, "sources": []},
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.run_doctor_smoke_check",
        lambda sandbox_root: ("pass", "Smoke run completed."),
    )

    report = build_doctor_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
        desktop_shell_dir=tmp_path / "desktop",
    )

    statuses = {check.check_id: check.status for check in report.checks}
    assert statuses["word_app"] == "fail"
    assert report.overall_status == "fail"


def test_build_doctor_report_returns_pass_when_core_checks_succeed(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_word_app",
        lambda: Path("/Applications/Microsoft Word.app"),
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_bun_binary",
        lambda: "/opt/homebrew/bin/bun",
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_provider_config_state",
        lambda: {"configured": True, "sources": ["OPENAI_API_KEY"]},
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.run_doctor_smoke_check",
        lambda sandbox_root: ("pass", "Smoke run completed."),
    )

    report = build_doctor_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
        desktop_shell_dir=tmp_path / "desktop",
    )

    statuses = {check.check_id: check.status for check in report.checks}
    assert statuses["word_app"] == "pass"
    assert statuses["provider_config"] == "pass"
    assert statuses["smoke_run"] == "pass"
    assert report.overall_status == "pass"


def test_build_doctor_report_warns_when_desktop_shell_dependencies_are_missing(
    monkeypatch,
    tmp_path: Path,
):
    desktop_dir = tmp_path / "desktop"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    (desktop_dir / "package.json").write_text('{"name":"officex-desktop"}', encoding="utf-8")

    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_word_app",
        lambda: Path("/Applications/Microsoft Word.app"),
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_bun_binary",
        lambda: "/opt/homebrew/bin/bun",
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_provider_config_state",
        lambda: {"configured": True, "sources": ["OPENAI_API_KEY"]},
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.run_doctor_smoke_check",
        lambda sandbox_root: ("pass", "Smoke run completed."),
    )

    report = build_doctor_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
        desktop_shell_dir=desktop_dir,
    )

    statuses = {check.check_id: check.status for check in report.checks}
    assert statuses["desktop_shell"] == "warning"
    assert report.overall_status == "warning"


def test_run_doctor_smoke_check_passes_before_cleanup(monkeypatch, tmp_path: Path):
    def fake_run_docx_mvp(
        *,
        run_id: str,
        sandbox_root: Path,
        source_path: Path,
        baseline_manifest_path: Path,
        write_contract_path: Path,
        approval_mode: str,
    ):
        candidate_dir = sandbox_root / run_id / "candidate"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        candidate_path = candidate_dir / "candidate.docx"
        candidate_path.write_text("ok", encoding="utf-8")
        return SimpleNamespace(
            candidate_docx=candidate_path,
            validation_error_count=0,
        )

    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.run_docx_mvp",
        fake_run_docx_mvp,
    )

    status, message = run_doctor_smoke_check(tmp_path / "sandboxes")

    assert status == "pass"
    assert message == "Smoke run completed."


def test_persist_doctor_report_writes_archive_and_latest_files(monkeypatch, tmp_path: Path):
    settings_dir = tmp_path / "machine-settings"
    monkeypatch.setenv("OFFICEX_SETTINGS_DIR", str(settings_dir))
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_word_app",
        lambda: Path("/Applications/Microsoft Word.app"),
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_bun_binary",
        lambda: "/opt/homebrew/bin/bun",
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.detect_provider_config_state",
        lambda: {"configured": True, "sources": ["OPENAI_API_KEY"]},
    )
    monkeypatch.setattr(
        "tools.report_scaffold_v3.doctor_runtime.run_doctor_smoke_check",
        lambda sandbox_root: ("pass", "Smoke run completed."),
    )

    report = build_doctor_report(
        workspace_root=tmp_path / "workspace",
        sandbox_root=tmp_path / "sandboxes",
        desktop_shell_dir=tmp_path / "desktop",
    )
    persisted = persist_doctor_report(report)

    assert persisted.report_json_path is not None
    assert persisted.report_markdown_path is not None
    assert persisted.report_json_path.exists()
    assert persisted.report_markdown_path.exists()
    assert (settings_dir / "reports" / "doctor" / "latest.json").exists()
    assert (settings_dir / "reports" / "doctor" / "latest.md").exists()
