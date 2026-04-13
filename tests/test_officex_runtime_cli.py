import json
from pathlib import Path

from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app


def test_officex_sandbox_create_writes_manifest(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "sandbox",
            "create",
            "--run-id",
            "demo-run",
            "--sandbox-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    sandbox_dir = tmp_path / "demo-run"
    assert sandbox_dir.exists()
    assert (sandbox_dir / "runtime" / "sandbox_manifest.json").exists()
    assert (sandbox_dir / "input" / "officex_docx_mvp_template.docx").exists()


def test_officex_task_run_docx_mvp_writes_reports(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "runtime-demo",
            "--sandbox-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    sandbox_dir = tmp_path / "runtime-demo"
    reports_dir = sandbox_dir / "reports"
    runtime_dir = sandbox_dir / "runtime"
    candidate_dir = sandbox_dir / "candidate"

    assert (runtime_dir / "task_packet.json").exists()
    assert (reports_dir / "validation.json").exists()
    assert (reports_dir / "candidate_audit.json").exists()
    assert (reports_dir / "stage_history_review.json").exists()
    assert (reports_dir / "run_event_log.json").exists()
    assert (reports_dir / "run_summary.json").exists()

    run_summary = json.loads((reports_dir / "run_summary.json").read_text(encoding="utf-8"))
    assert Path(run_summary["candidate_docx"]).exists()
    assert Path(run_summary["sandbox_root"]) == sandbox_dir
    assert any(candidate_dir.iterdir())
