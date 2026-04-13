import pytest
from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.prompt_runtime import (
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
