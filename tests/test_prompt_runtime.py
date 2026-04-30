import pytest
from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.prompt_runtime import (
    compile_officex_prompt_bundle,
    compose_officex_prompt,
    list_officex_roles,
)


def test_list_officex_roles_contains_expected_core_roles():
    roles = list_officex_roles()

    assert "orchestrator" in roles
    assert "patch_engineer" in roles
    assert "validation_engineer" in roles


def test_compose_officex_prompt_includes_cognition_by_default():
    content = compose_officex_prompt("orchestrator")

    assert "You are `OfficeX`." in content
    assert "# Orchestrator Prompt" in content


def test_compose_officex_prompt_can_render_role_only():
    content = compose_officex_prompt("orchestrator", include_cognition=False)

    assert "You are `OfficeX`." not in content
    assert "# Orchestrator Prompt" in content


def test_compose_officex_prompt_rejects_unknown_role():
    with pytest.raises(ValueError):
        compose_officex_prompt("unknown-role")


def test_compile_officex_prompt_bundle_emits_manifest_resolved_refs_and_trace():
    bundle = compile_officex_prompt_bundle("orchestrator")

    assert bundle.role == "orchestrator"
    assert bundle.include_cognition is True
    assert [entry.ref for entry in bundle.prompt_manifest] == [
        "prompts/OFFICEX_COGNITION.md",
        "prompts/ORCHESTRATOR.md",
    ]
    assert [entry.layer for entry in bundle.prompt_manifest] == ["cognition", "role"]
    assert bundle.resolved_rule_refs[0].source_path.name == "OFFICEX_COGNITION.md"
    assert bundle.resolved_rule_refs[1].source_path.name == "ORCHESTRATOR.md"
    assert bundle.resolved_rule_refs[0].section_title == "OfficeX Cognition"
    assert bundle.resolved_rule_refs[1].section_title == "Orchestrator Prompt"
    assert bundle.prompt_trace_record.prompt_source_refs == [
        "prompts/OFFICEX_COGNITION.md",
        "prompts/ORCHESTRATOR.md",
    ]
    assert len(bundle.prompt_trace_record.compiled_prompt_sha256) == 64
    assert "You are `OfficeX`." in bundle.compiled_prompt_debug
    assert "# Orchestrator Prompt" in bundle.compiled_prompt_debug


def test_compile_officex_prompt_bundle_supports_role_only():
    bundle = compile_officex_prompt_bundle("orchestrator", include_cognition=False)

    assert [entry.ref for entry in bundle.prompt_manifest] == ["prompts/ORCHESTRATOR.md"]
    assert [entry.layer for entry in bundle.prompt_manifest] == ["role"]
    assert len(bundle.resolved_rule_refs) == 1
    assert bundle.resolved_rule_refs[0].section_title == "Orchestrator Prompt"
    assert "You are `OfficeX`." not in bundle.compiled_prompt_debug


def test_officex_prompt_show_command_outputs_composed_prompt():
    runner = CliRunner()

    result = runner.invoke(app, ["officex", "prompt", "show", "--role", "orchestrator"])

    assert result.exit_code == 0
    assert "You are `OfficeX`." in result.stdout
    assert "# Orchestrator Prompt" in result.stdout


def test_officex_prompt_show_command_as_json_outputs_machine_readable_prompt():
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["officex", "prompt", "show", "--role", "orchestrator", "--as-json"],
    )

    assert result.exit_code == 0
    assert '"role": "orchestrator"' in result.stdout
    assert '"include_cognition": true' in result.stdout.lower()
    assert '"prompt":' in result.stdout


def test_officex_prompt_show_command_rejects_unknown_role():
    runner = CliRunner()

    result = runner.invoke(app, ["officex", "prompt", "show", "--role", "unknown-role"])

    assert result.exit_code == 1
    assert "Unknown OfficeX role" in result.stdout
