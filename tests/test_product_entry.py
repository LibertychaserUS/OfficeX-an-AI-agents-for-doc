from __future__ import annotations

from pathlib import Path

from tools.report_scaffold_v3 import product_entry


def test_product_entry_launches_app_when_no_args(monkeypatch):
    launched: list[Path] = []

    def fake_launch_app() -> Path:
        path = Path("/tmp/officex-desktop-app")
        launched.append(path)
        return path

    monkeypatch.setattr(product_entry, "launch_officex_app", fake_launch_app)

    exit_code = product_entry.main([])

    assert exit_code == 0
    assert launched == [Path("/tmp/officex-desktop-app")]


def test_product_entry_routes_doctor_to_officex_cli(monkeypatch):
    captured: list[list[str]] = []

    def fake_invoke_cli(argv: list[str]) -> int:
        captured.append(argv)
        return 0

    monkeypatch.setattr(product_entry, "_invoke_officex_cli", fake_invoke_cli)

    exit_code = product_entry.main(["doctor", "--as-json"])

    assert exit_code == 0
    assert captured == [["doctor", "--as-json"]]


def test_product_entry_routes_render_boundary_to_officex_cli(monkeypatch):
    captured: list[list[str]] = []

    def fake_invoke_cli(argv: list[str]) -> int:
        captured.append(argv)
        return 0

    monkeypatch.setattr(product_entry, "_invoke_officex_cli", fake_invoke_cli)

    exit_code = product_entry.main(["render-boundary", "--as-json"])

    assert exit_code == 0
    assert captured == [["render-boundary", "--as-json"]]


def test_product_entry_routes_runtime_commands_to_existing_officex_tree(monkeypatch):
    captured: list[list[str]] = []

    def fake_invoke_cli(argv: list[str]) -> int:
        captured.append(argv)
        return 0

    monkeypatch.setattr(product_entry, "_invoke_officex_cli", fake_invoke_cli)

    exit_code = product_entry.main(["runtime", "task", "inspect", "--run-id", "demo"])

    assert exit_code == 0
    assert captured == [["task", "inspect", "--run-id", "demo"]]


def test_product_entry_runtime_help_uses_single_officex_prefix(capsys):
    exit_code = product_entry.main(["runtime", "task", "inspect", "--help"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Usage: officex task inspect" in captured.out
    assert "officex officex" not in captured.out


def test_invoke_officex_cli_propagates_click_exit_codes(monkeypatch):
    class FakeCommand:
        def main(self, *args, **kwargs):
            from click.exceptions import Exit as ClickExit

            raise ClickExit(2)

    monkeypatch.setattr(product_entry, "get_command", lambda app: FakeCommand())

    exit_code = product_entry._invoke_officex_cli(["doctor", "--as-json"])

    assert exit_code == 2


def test_invoke_officex_cli_propagates_integer_return_values(monkeypatch):
    class FakeCommand:
        def main(self, *args, **kwargs):
            return 3

    monkeypatch.setattr(product_entry, "get_command", lambda app: FakeCommand())

    exit_code = product_entry._invoke_officex_cli(["doctor", "--as-json"])

    assert exit_code == 3
