from __future__ import annotations

import sys
from typing import Sequence

from click.exceptions import Exit as ClickExit
from typer.main import get_command

from .cli import officex_app


def _invoke_officex_cli(argv: list[str]) -> int:
    command = get_command(officex_app)
    try:
        result = command.main(args=argv, prog_name="officex", standalone_mode=False)
    except ClickExit as exc:
        return int(exc.exit_code or 1)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 1
    return result if isinstance(result, int) else 0


def _show_banner() -> None:
    from .cli_banner import render_startup_banner
    render_startup_banner()


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        _show_banner()
        return 0
    if args[0] == "runtime":
        return _invoke_officex_cli(args[1:])
    if args[0] in {"doctor", "render-boundary"}:
        return _invoke_officex_cli(args)
    return _invoke_officex_cli(args)


def entrypoint() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    entrypoint()
