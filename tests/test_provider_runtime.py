import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.officex_runtime import run_docx_mvp
from tools.report_scaffold_v3.paths import (
    DEFAULT_BASELINE_MANIFEST,
    DEFAULT_BUILD_SOURCE,
    DEFAULT_WRITE_CONTRACT_MANIFEST,
)
from tools.report_scaffold_v3.provider_runtime import (
    build_provider_request_envelope,
    build_provider_prompt_binding,
    list_provider_ids,
    parse_provider_config_field_assignments,
    resolve_provider_model,
)


def test_list_provider_ids_contains_expected_initial_providers():
    provider_ids = list_provider_ids()

    assert "openai" in provider_ids
    assert "anthropic" in provider_ids
    assert "compatible_local" in provider_ids


def test_build_provider_prompt_binding_uses_default_model_and_cognition():
    binding = build_provider_prompt_binding("openai", role="orchestrator")

    assert binding.model_id == "gpt-5.4"
    assert binding.provider_id == "openai"
    assert [entry.ref for entry in binding.prompt_manifest] == [
        "prompts/OFFICEX_COGNITION.md",
        "prompts/ORCHESTRATOR.md",
    ]
    assert len(binding.resolved_rule_refs) == 2
    assert binding.prompt_trace_record.prompt_source_refs == [
        "prompts/OFFICEX_COGNITION.md",
        "prompts/ORCHESTRATOR.md",
    ]
    assert binding.compiled_prompt_debug == binding.prompt
    assert "You are `OfficeX`." in binding.prompt
    assert "# Orchestrator Prompt" in binding.prompt


def test_build_provider_prompt_binding_can_render_role_only():
    binding = build_provider_prompt_binding(
        "anthropic",
        role="orchestrator",
        include_cognition=False,
    )

    assert [entry.ref for entry in binding.prompt_manifest] == ["prompts/ORCHESTRATOR.md"]
    assert len(binding.resolved_rule_refs) == 1
    assert "You are `OfficeX`." not in binding.prompt
    assert "# Orchestrator Prompt" in binding.prompt


def test_build_provider_prompt_binding_rejects_unknown_model():
    with pytest.raises(ValueError):
        build_provider_prompt_binding(
            "openai",
            role="orchestrator",
            model_id="missing-model",
        )


def test_resolve_provider_model_supports_explicit_local_model():
    model = resolve_provider_model("compatible_local", model_id="user-configured-local")

    assert model.model_id == "user-configured-local"
    assert model.supports_structured_output is False
    assert model.supports_tool_calls is False


def test_build_provider_prompt_binding_merges_provider_and_model_notes_in_order():
    binding = build_provider_prompt_binding("openai", role="orchestrator")

    assert binding.notes[:2] == [
        "Initial OfficeX baseline for structured planning, generation, and review.",
        "Actual deployed model choice remains user-configurable at runtime.",
    ]
    assert binding.notes[-1] == "Validate final document changes through deterministic mutation and audit."


def test_parse_provider_config_field_assignments_parses_name_value_pairs():
    parsed = parse_provider_config_field_assignments(
        ["api_key=secret", "model_id=gpt-5.4", "base_url_optional=https://example.test"]
    )

    assert parsed == {
        "api_key": "secret",
        "model_id": "gpt-5.4",
        "base_url_optional": "https://example.test",
    }


def test_parse_provider_config_field_assignments_rejects_duplicate_fields():
    with pytest.raises(ValueError):
        parse_provider_config_field_assignments(["api_key=secret", "api_key=other"])


def test_parse_provider_config_field_assignments_rejects_invalid_shape():
    with pytest.raises(ValueError):
        parse_provider_config_field_assignments(["api_key"])


def test_build_provider_request_envelope_uses_task_packet_path(tmp_path: Path):
    report = run_docx_mvp(
        run_id="provider-envelope-path",
        sandbox_root=tmp_path,
        source_path=DEFAULT_BUILD_SOURCE,
        baseline_manifest_path=DEFAULT_BASELINE_MANIFEST,
        write_contract_path=DEFAULT_WRITE_CONTRACT_MANIFEST,
        approval_mode="ask_every_conflict",
    )

    envelope = build_provider_request_envelope(
        "openai",
        role="orchestrator",
        task_packet_path=report.task_packet_path,
        sandbox_root=tmp_path,
        config_field_assignments=["api_key=secret", "model_id=gpt-5.4"],
        response_contract_kind="plan_object",
    )

    assert envelope.provider_id == "openai"
    assert envelope.task_packet_id == "provider-envelope-path-task"
    assert envelope.dispatch_mode == "dry_run"
    assert envelope.required_config_fields == ["api_key", "model_id"]
    assert envelope.provided_config_fields == ["api_key", "model_id"]
    assert envelope.response_contract_kind == "plan_object"
    assert envelope.prompt_manifest[0].ref == "prompts/OFFICEX_COGNITION.md"
    assert envelope.resolved_rule_refs[1].section_title == "Orchestrator Prompt"
    assert envelope.prompt_trace_record.prompt_source_refs == [
        "prompts/OFFICEX_COGNITION.md",
        "prompts/ORCHESTRATOR.md",
    ]
    assert envelope.compiled_prompt_debug == envelope.system_prompt
    assert "You are `OfficeX`." in envelope.system_prompt


def test_build_provider_request_envelope_uses_run_id_resolution(tmp_path: Path):
    run_docx_mvp(
        run_id="provider-envelope-run",
        sandbox_root=tmp_path,
        source_path=DEFAULT_BUILD_SOURCE,
        baseline_manifest_path=DEFAULT_BASELINE_MANIFEST,
        write_contract_path=DEFAULT_WRITE_CONTRACT_MANIFEST,
        approval_mode="ask_every_conflict",
    )

    envelope = build_provider_request_envelope(
        "anthropic",
        role="orchestrator",
        run_id="provider-envelope-run",
        sandbox_root=tmp_path,
        config_field_assignments=["api_key=secret", "model_id=claude-opus-4-1"],
        response_contract_kind="review_findings",
    )

    assert envelope.provider_id == "anthropic"
    assert envelope.task_packet_id == "provider-envelope-run-task"
    assert envelope.response_contract_kind == "review_findings"


def test_build_provider_request_envelope_rejects_unknown_role(tmp_path: Path):
    report = run_docx_mvp(
        run_id="provider-envelope-role",
        sandbox_root=tmp_path,
        source_path=DEFAULT_BUILD_SOURCE,
        baseline_manifest_path=DEFAULT_BASELINE_MANIFEST,
        write_contract_path=DEFAULT_WRITE_CONTRACT_MANIFEST,
        approval_mode="ask_every_conflict",
    )

    with pytest.raises(ValueError):
        build_provider_request_envelope(
            "openai",
            role="missing-role",
            task_packet_path=report.task_packet_path,
            sandbox_root=tmp_path,
        )


def test_build_provider_request_envelope_rejects_unknown_config_field(tmp_path: Path):
    report = run_docx_mvp(
        run_id="provider-envelope-config",
        sandbox_root=tmp_path,
        source_path=DEFAULT_BUILD_SOURCE,
        baseline_manifest_path=DEFAULT_BASELINE_MANIFEST,
        write_contract_path=DEFAULT_WRITE_CONTRACT_MANIFEST,
        approval_mode="ask_every_conflict",
    )

    with pytest.raises(ValueError):
        build_provider_request_envelope(
            "openai",
            role="orchestrator",
            task_packet_path=report.task_packet_path,
            sandbox_root=tmp_path,
            config_field_assignments=["unexpected=value"],
        )


def test_build_provider_request_envelope_requires_task_resolution_input():
    with pytest.raises(ValueError):
        build_provider_request_envelope(
            "openai",
            role="orchestrator",
            sandbox_root=Path("/tmp/officex-provider-envelope-missing"),
        )


def test_officex_provider_list_command_outputs_known_provider_ids():
    runner = CliRunner()

    result = runner.invoke(app, ["officex", "provider", "list"])

    assert result.exit_code == 0
    assert "`openai`" in result.stdout
    assert "`anthropic`" in result.stdout
    assert "status: `active`" in result.stdout


def test_officex_provider_show_command_outputs_binding_and_prompt():
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "show",
            "--provider",
            "openai",
            "--role",
            "orchestrator",
            "--include-prompt",
        ],
    )

    assert result.exit_code == 0
    assert "Provider: `openai`" in result.stdout
    assert "Model: `gpt-5.4`" in result.stdout
    assert "# Orchestrator Prompt" in result.stdout


def test_officex_provider_show_command_as_json_outputs_machine_readable_binding():
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["officex", "provider", "show", "--provider", "openai", "--role", "orchestrator", "--as-json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["provider_id"] == "openai"
    assert payload["model_id"] == "gpt-5.4"


def test_officex_provider_show_command_supports_role_only_and_explicit_model():
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "show",
            "--provider",
            "anthropic",
            "--role",
            "orchestrator",
            "--model",
            "claude-sonnet-4-5",
            "--role-only",
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["model_id"] == "claude-sonnet-4-5"
    assert payload["include_cognition"] is False
    assert "You are `OfficeX`." not in payload["prompt"]


def test_officex_provider_show_command_rejects_unknown_role():
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["officex", "provider", "show", "--provider", "openai", "--role", "missing-role"],
    )

    assert result.exit_code == 1
    assert "Unknown OfficeX role prompt" in result.stdout


def test_officex_provider_build_request_command_outputs_machine_readable_envelope(tmp_path: Path):
    runner = CliRunner()
    run_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "provider-build-request",
            "--sandbox-root",
            str(tmp_path),
        ],
    )
    assert run_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "build-request",
            "--provider",
            "openai",
            "--role",
            "orchestrator",
            "--run-id",
            "provider-build-request",
            "--sandbox-root",
            str(tmp_path),
            "--config-field",
            "api_key=secret",
            "--config-field",
            "model_id=gpt-5.4",
            "--response-contract-kind",
            "plan_object",
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["provider_id"] == "openai"
    assert payload["task_packet_id"] == "provider-build-request-task"
    assert payload["required_config_fields"] == ["api_key", "model_id"]
    assert payload["provided_config_fields"] == ["api_key", "model_id"]
    assert payload["response_contract_kind"] == "plan_object"
    assert payload["prompt_manifest"][0]["ref"] == "prompts/OFFICEX_COGNITION.md"
    assert payload["resolved_rule_refs"][1]["section_title"] == "Orchestrator Prompt"
    assert payload["prompt_trace_record"]["prompt_source_refs"] == [
        "prompts/OFFICEX_COGNITION.md",
        "prompts/ORCHESTRATOR.md",
    ]
    assert payload["compiled_prompt_debug"] == payload["system_prompt"]


def test_officex_provider_build_request_command_supports_task_packet_path_and_explicit_model(tmp_path: Path):
    runner = CliRunner()
    run_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "provider-build-request-path",
            "--sandbox-root",
            str(tmp_path),
        ],
    )
    assert run_result.exit_code == 0
    task_packet = tmp_path / "provider-build-request-path" / "runtime" / "task_packet.json"

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "build-request",
            "--provider",
            "anthropic",
            "--role",
            "orchestrator",
            "--model",
            "claude-sonnet-4-5",
            "--task-packet",
            str(task_packet),
            "--config-field",
            "api_key=secret",
            "--config-field",
            "model_id=claude-sonnet-4-5",
        ],
    )

    assert result.exit_code == 0
    assert "OfficeX Provider Request Envelope" in result.stdout
    assert "Response contract: `plan_object`" in result.stdout
    assert "Model: `claude-sonnet-4-5`" in result.stdout
    assert "Prompt Manifest" in result.stdout
    assert "`role` -> `prompts/ORCHESTRATOR.md` (`orchestrator`)" in result.stdout


def test_officex_provider_build_request_command_rejects_invalid_config_field(tmp_path: Path):
    runner = CliRunner()
    run_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "provider-build-request-invalid",
            "--sandbox-root",
            str(tmp_path),
        ],
    )
    assert run_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "build-request",
            "--provider",
            "openai",
            "--role",
            "orchestrator",
            "--run-id",
            "provider-build-request-invalid",
            "--sandbox-root",
            str(tmp_path),
            "--config-field",
            "unexpected=value",
        ],
    )

    assert result.exit_code == 1
    assert "Unknown OfficeX config field" in result.stdout


def test_officex_provider_build_request_command_rejects_unknown_model(tmp_path: Path):
    runner = CliRunner()
    run_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "provider-build-request-model",
            "--sandbox-root",
            str(tmp_path),
        ],
    )
    assert run_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "build-request",
            "--provider",
            "openai",
            "--role",
            "orchestrator",
            "--model",
            "missing-model",
            "--run-id",
            "provider-build-request-model",
            "--sandbox-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 1
    assert "Unknown model `missing-model`" in result.stdout


def test_officex_provider_build_request_command_rejects_unknown_role(tmp_path: Path):
    runner = CliRunner()
    run_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "provider-build-request-role",
            "--sandbox-root",
            str(tmp_path),
        ],
    )
    assert run_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "build-request",
            "--provider",
            "openai",
            "--role",
            "missing-role",
            "--run-id",
            "provider-build-request-role",
            "--sandbox-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 1
    assert "Unknown OfficeX role prompt" in result.stdout


def test_officex_provider_build_request_command_rejects_missing_task_resolution_input():
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "officex",
            "provider",
            "build-request",
            "--provider",
            "openai",
            "--role",
            "orchestrator",
        ],
    )

    assert result.exit_code == 1
    assert "Provide either `--task-packet` or `--run-id`." in result.stdout


def test_officex_provider_show_command_rejects_unknown_provider():
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["officex", "provider", "show", "--provider", "missing-provider"],
    )

    assert result.exit_code == 1
    assert "Unknown OfficeX provider" in result.stdout
