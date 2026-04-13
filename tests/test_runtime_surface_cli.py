import json
from pathlib import Path

from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app


def test_officex_workspace_init_creates_manifest_and_dirs(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "workspace",
            "init",
            "--workspace-id",
            "demo-workspace",
            "--workspace-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    workspace_dir = tmp_path / "demo-workspace"
    assert workspace_dir.exists()
    assert (workspace_dir / "runtime" / "workspace_manifest.json").exists()
    assert (workspace_dir / "sandboxes").exists()


def test_officex_workspace_init_as_json_outputs_machine_readable_payload(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "workspace",
            "init",
            "--workspace-id",
            "json-workspace",
            "--workspace-root",
            str(tmp_path),
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["workspace_id"] == "json-workspace"
    assert payload["active_page_profile"] == "a4"


def test_officex_workspace_init_rejects_existing_workspace(tmp_path: Path):
    runner = CliRunner()
    workspace_args = [
        "officex",
        "workspace",
        "init",
        "--workspace-id",
        "existing-workspace",
        "--workspace-root",
        str(tmp_path),
    ]

    first_result = runner.invoke(app, workspace_args)
    second_result = runner.invoke(app, workspace_args)

    assert first_result.exit_code == 0
    assert second_result.exit_code == 1
    assert "Workspace already exists" in second_result.stdout


def test_officex_sandbox_create_as_json_outputs_manifest_payload(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "sandbox",
            "create",
            "--run-id",
            "json-sandbox",
            "--sandbox-root",
            str(tmp_path),
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["run_id"] == "json-sandbox"
    assert payload["sandbox_root"].endswith("/json-sandbox")


def test_officex_task_inspect_reads_task_packet_from_sandbox_run(tmp_path: Path):
    runner = CliRunner()

    run_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "inspect-demo",
            "--sandbox-root",
            str(tmp_path),
        ],
    )
    assert run_result.exit_code == 0

    inspect_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "inspect",
            "--run-id",
            "inspect-demo",
            "--sandbox-root",
            str(tmp_path),
            "--as-json",
        ],
    )

    assert inspect_result.exit_code == 0
    payload = json.loads(inspect_result.stdout)
    assert payload["task_packet_id"] == "inspect-demo-task"
    assert payload["approval_mode"] == "ask_every_conflict"


def test_officex_task_run_docx_mvp_as_json_outputs_run_summary(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "json-run",
            "--sandbox-root",
            str(tmp_path),
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["run_id"] == "json-run"
    assert Path(payload["candidate_docx"]).exists()


def test_officex_task_inspect_requires_resolution_input():
    runner = CliRunner()

    result = runner.invoke(app, ["officex", "task", "inspect"])

    assert result.exit_code == 1
    assert "Provide either `--task-packet` or `--run-id`." in result.stdout


def test_officex_task_inspect_rejects_invalid_task_packet_schema(tmp_path: Path):
    runner = CliRunner()
    task_packet = tmp_path / "task_packet.json"
    task_packet.write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "inspect",
            "--task-packet",
            str(task_packet),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid OfficeX task packet schema" in result.stdout


def test_officex_agent_list_and_show_commands_use_catalog():
    runner = CliRunner()

    list_result = runner.invoke(app, ["officex", "agent", "list"])
    assert list_result.exit_code == 0
    assert "`orchestrator`" in list_result.stdout
    assert "`validation_review_auditor`" in list_result.stdout

    show_result = runner.invoke(
        app,
        [
            "officex",
            "agent",
            "show",
            "--agent",
            "patch_assembly_engineer",
            "--as-json",
        ],
    )
    assert show_result.exit_code == 0
    payload = json.loads(show_result.stdout)
    assert payload["runtime_role"] == "patch_and_assembly_engineer"
    assert "patch_engineer" in payload["prompt_roles"]


def test_officex_agent_list_as_json_outputs_machine_readable_catalog():
    runner = CliRunner()

    result = runner.invoke(app, ["officex", "agent", "list", "--as-json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["catalog_id"] == "officex-agent-catalog"
    assert any(agent["agent_id"] == "validation_review_auditor" for agent in payload["agents"])


def test_officex_agent_show_rejects_unknown_agent():
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["officex", "agent", "show", "--agent", "missing-agent"],
    )

    assert result.exit_code == 1
    assert "Unknown OfficeX agent" in result.stdout


def test_officex_trace_checkpoint_writes_checkpoint_and_catalog(tmp_path: Path):
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "trace",
            "checkpoint",
            "--title",
            "Runtime surface test checkpoint",
            "--summary-line",
            "Added trace checkpoint command coverage.",
            "--verification-line",
            "CLI test pass.",
            "--trace-dir",
            str(tmp_path),
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    checkpoint_path = Path(payload["checkpoint_path"])
    assert checkpoint_path.exists()
    assert (tmp_path / "checkpoint_catalog.json").exists()
    assert (tmp_path / "checkpoint_catalog_summary.md").exists()
    assert payload["checkpoint_id"] == "CHECKPOINT_01"
