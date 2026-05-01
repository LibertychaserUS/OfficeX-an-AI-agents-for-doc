from __future__ import annotations

from pathlib import Path

from tools.report_scaffold_v3 import product_entry


def test_product_entry_shows_banner_when_no_args(monkeypatch):
    banner_shown = []

    def fake_show_banner() -> None:
        banner_shown.append(True)

    monkeypatch.setattr(product_entry, "_show_banner", fake_show_banner)

    exit_code = product_entry.main([])

    assert exit_code == 0
    assert banner_shown == [True]


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
    # Strip ANSI escape codes for comparison
    import re
    clean_out = re.sub(r"\x1b\[[0-9;]*m", "", captured.out)

    assert exit_code == 0
    assert "officex task inspect" in clean_out.lower() or "usage" in clean_out.lower()
    assert "officex officex" not in clean_out


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
