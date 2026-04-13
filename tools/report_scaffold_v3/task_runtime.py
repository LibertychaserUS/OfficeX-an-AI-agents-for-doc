from __future__ import annotations

from pathlib import Path

from .models import OfficeXTaskPacket
from .paths import SANDBOXES_DIR
from .runtime_common import (
    load_runtime_structured_model,
    render_bullet_block,
)


def render_task_packet_markdown(packet: OfficeXTaskPacket) -> str:
    lines = [
        "# OfficeX Task Packet",
        "",
        f"- Task packet ID: `{packet.task_packet_id}`",
        f"- Goal: {packet.goal}",
        f"- Task family: `{packet.task_family}`",
        f"- Active workspace: `{packet.active_workspace}`",
        f"- Approval mode: `{packet.approval_mode}`",
        f"- Publish gate: `{packet.publish_gate}`",
        "",
        "## Allowed Surfaces",
        "",
    ]
    lines.extend(render_bullet_block(packet.allowed_surfaces))
    lines.extend(["", "## Constraints", ""])
    lines.extend(render_bullet_block(packet.constraints))
    lines.extend(["", "## Acceptance Gates", ""])
    lines.extend(render_bullet_block(packet.acceptance_gates))
    return "\n".join(lines)


def resolve_task_packet_path(
    *,
    task_packet_path: Path | None = None,
    run_id: str | None = None,
    sandbox_root: Path = SANDBOXES_DIR,
) -> Path:
    if task_packet_path is None and run_id is None:
        raise ValueError("Provide either `--task-packet` or `--run-id`.")

    if task_packet_path is not None:
        resolved = task_packet_path.expanduser().resolve()
    else:
        resolved = (
            sandbox_root.expanduser().resolve()
            / run_id
            / "runtime"
            / "task_packet.json"
        )

    if not resolved.exists():
        raise FileNotFoundError(f"Task packet not found: {resolved}")
    return resolved


def load_task_packet(
    *,
    task_packet_path: Path | None = None,
    run_id: str | None = None,
    sandbox_root: Path = SANDBOXES_DIR,
) -> OfficeXTaskPacket:
    resolved = resolve_task_packet_path(
        task_packet_path=task_packet_path,
        run_id=run_id,
        sandbox_root=sandbox_root,
    )
    try:
        return load_runtime_structured_model(resolved, OfficeXTaskPacket)
    except ValueError as exc:
        raise ValueError(f"Invalid OfficeX task packet schema: {resolved}") from exc
