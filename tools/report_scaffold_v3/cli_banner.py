"""OfficeX CLI brand banner, startup display, and environment scan.

Renders a polished startup screen when `officex` is invoked without
arguments: product identity, auto-detected environment status,
and available command families.
"""

from __future__ import annotations

import importlib
import os
import platform
import shutil

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


COMMAND_FAMILIES = [
    ("generate", "Generate a document from a prompt (end-to-end)"),
    ("doctor", "Full environment readiness check"),
    ("audit visual", "Render docx to PNG and run visual QA"),
    ("task run-docx-mvp", "Run deterministic docx generation pipeline"),
    ("task apply-patch-bundle", "Apply deterministic document patches"),
    ("provider list", "List configured providers"),
    ("prompt show", "Display composed role prompt"),
    ("agent list", "List registered agents"),
    ("trace checkpoint", "Create a trace checkpoint"),
]

REQUIRED_PACKAGES = [
    ("docx", "python-docx"),
    ("pydantic", "pydantic"),
    ("yaml", "PyYAML"),
    ("PIL", "Pillow"),
    ("typer", "typer"),
    ("rich", "rich"),
]

OPTIONAL_PACKAGES = [
    ("fitz", "pymupdf", "PDF-to-PNG rendering"),
    ("numpy", "numpy", "Visual audit checks"),
    ("openai", "openai", "AI provider dispatch"),
]


def _check_package(import_name: str) -> bool:
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def _find_soffice() -> str | None:
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    for path in (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/opt/homebrew/bin/soffice",
    ):
        if os.path.isfile(path):
            return path
    return None


def _scan_environment() -> list[tuple[str, str, str]]:
    """Scan environment and return list of (component, status_icon, detail)."""
    items: list[tuple[str, str, str]] = []

    # Python
    py_ver = platform.python_version()
    py_ok = tuple(int(x) for x in py_ver.split(".")[:2]) >= (3, 11)
    items.append((
        "Python",
        "[green]OK[/green]" if py_ok else "[red]!!![/red]",
        f"{py_ver}" + ("" if py_ok else " (need 3.11+)"),
    ))

    # LibreOffice
    soffice = _find_soffice()
    if soffice:
        items.append(("LibreOffice", "[green]OK[/green]", "visual audit available"))
    else:
        items.append((
            "LibreOffice",
            "[yellow]--[/yellow]",
            "not found. Install: [cyan]brew install --cask libreoffice[/cyan]",
        ))

    # Required packages
    missing_required = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        if not _check_package(import_name):
            missing_required.append(pip_name)
    if missing_required:
        items.append((
            "Core deps",
            "[red]!!![/red]",
            f"missing: [cyan]pip install {' '.join(missing_required)}[/cyan]",
        ))
    else:
        items.append(("Core deps", "[green]OK[/green]", "all present"))

    # Optional packages
    missing_optional = []
    for import_name, pip_name, purpose in OPTIONAL_PACKAGES:
        if not _check_package(import_name):
            missing_optional.append(f"{pip_name} ({purpose})")
    if missing_optional:
        items.append((
            "Optional",
            "[yellow]--[/yellow]",
            "missing: " + ", ".join(missing_optional),
        ))

    # API key
    has_key = bool(os.environ.get("OFFICEX_PROVIDER_API_KEY"))
    if has_key:
        items.append(("API key", "[green]OK[/green]", "OFFICEX_PROVIDER_API_KEY set"))
    else:
        items.append((
            "API key",
            "[yellow]--[/yellow]",
            "set [cyan]OFFICEX_PROVIDER_API_KEY[/cyan] for AI features",
        ))

    return items


def render_startup_banner(*, version: str = "0.1.0") -> None:
    """Display the OfficeX CLI brand banner with environment scan."""
    console = Console()

    # Brand header
    header = Text()
    header.append("  OfficeX", style="bold cyan")
    header.append("  Document Operations System\n", style="dim")
    header.append(f"  v{version}", style="dim cyan")
    header.append(f"  |  Python {platform.python_version()}", style="dim")

    console.print()
    console.print(Panel(header, border_style="cyan", padding=(0, 1)))

    # Environment scan
    env_items = _scan_environment()
    env_table = Table(
        show_header=False,
        border_style="dim",
        padding=(0, 1),
        title="Environment",
        title_style="bold",
        min_width=60,
    )
    env_table.add_column("Component", style="dim", width=14)
    env_table.add_column("Status", width=6, justify="center")
    env_table.add_column("Detail")

    for component, status_icon, detail in env_items:
        env_table.add_row(component, status_icon, detail)

    console.print(env_table)

    # Command table
    cmd_table = Table(
        show_header=True,
        header_style="bold",
        border_style="dim",
        padding=(0, 2),
        title="Commands",
        title_style="bold",
    )
    cmd_table.add_column("Command", style="cyan", no_wrap=True)
    cmd_table.add_column("Description")

    for cmd, desc in COMMAND_FAMILIES:
        cmd_table.add_row(f"officex {cmd}", desc)

    console.print(cmd_table)

    # Usage hints
    console.print()
    console.print("  [dim]Run[/dim] [cyan]officex <command> --help[/cyan] [dim]for details[/dim]")
    console.print("  [dim]Add[/dim] [cyan]--as-json[/cyan] [dim]for machine-readable output[/dim]")
    console.print()
