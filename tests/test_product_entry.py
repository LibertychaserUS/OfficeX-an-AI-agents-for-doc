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


def test_officex_cli_reports_missing_option_without_traceback(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo.docx").write_bytes(b"")

    exit_code = product_entry.main(["audit", "visual", "--candidate-docx", "demo.docx"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Missing option '--output-dir'" in captured.err
    assert "Traceback" not in captured.err + captured.out


def test_officex_cli_rejects_missing_input_file(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)

    exit_code = product_entry.main(
        ["diff", "--a", "missing.docx", "--b", "missing.docx", "--output-dir", "out"]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "does not exist" in captured.err
    assert not (tmp_path / "out").exists()


def test_officex_cli_reports_unknown_command(capsys):
    exit_code = product_entry.main(["genrate"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "No such command 'genrate'" in captured.err
