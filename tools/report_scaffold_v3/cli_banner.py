"""OfficeX CLI brand banner and startup display.

Renders a polished startup screen when `officex` is invoked without
arguments, showing product identity, environment status, and available
command families.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


COMMAND_FAMILIES = [
    ("generate", "Generate a document from a prompt (end-to-end)"),
    ("doctor", "Environment readiness check"),
    ("render-boundary", "Renderer capability matrix"),
    ("workspace init", "Initialize a new workspace"),
    ("sandbox create", "Create an isolated sandbox"),
    ("task run-docx-mvp", "Run full docx generation pipeline"),
    ("task inspect", "Inspect task packet artifacts"),
    ("task apply-patch-bundle", "Apply deterministic document patches"),
    ("audit visual", "Render docx to PNG and run visual QA"),
    ("provider list", "List configured providers"),
    ("provider build-request", "Build provider request envelope"),
    ("prompt show", "Display composed role prompt"),
    ("agent list", "List registered agents"),
    ("trace checkpoint", "Create a trace checkpoint"),
]


def render_startup_banner(
    *,
    version: str = "0.1.0",
    python_version: str = "",
    renderer_available: bool = False,
    renderer_name: str = "",
    test_count: int | None = None,
) -> None:
    """Display the OfficeX CLI brand banner."""
    console = Console()

    # Brand header
    header = Text()
    header.append("  OfficeX", style="bold cyan")
    header.append("  Document Operations System\n", style="dim")
    header.append(f"  v{version}", style="dim cyan")
    if python_version:
        header.append(f"  |  Python {python_version}", style="dim")
    if renderer_available:
        header.append(f"  |  {renderer_name}", style="dim green")
    else:
        header.append("  |  No renderer", style="dim yellow")

    console.print()
    console.print(Panel(header, border_style="cyan", padding=(0, 1)))

    # Command table
    table = Table(
        show_header=True,
        header_style="bold",
        border_style="dim",
        padding=(0, 2),
        title="Available Commands",
        title_style="bold",
    )
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description")

    for cmd, desc in COMMAND_FAMILIES:
        table.add_row(f"officex {cmd}", desc)

    console.print(table)

    # Usage hint
    console.print()
    console.print("  [dim]Run[/dim] [cyan]officex <command> --help[/cyan] [dim]for details[/dim]")
    console.print("  [dim]Add[/dim] [cyan]--as-json[/cyan] [dim]for machine-readable output[/dim]")
    console.print()
