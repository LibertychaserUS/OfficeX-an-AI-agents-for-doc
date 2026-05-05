"""OfficeX — AI-powered document operations platform.

This is the public package alias. Internal implementation lives in
tools.report_scaffold_v3 for historical compatibility.

Usage:
    import officex
    from officex import generate_runtime, visual_audit, profile_runtime
"""

from tools.report_scaffold_v3 import (
    cli,
    cli_banner,
    cli_render,
    generate_runtime,
    long_generate_runtime,
    edit_runtime,
    diff_runtime,
    visual_audit,
    visual_audit_checks,
    profile_runtime,
    provider_adapter,
    provider_runtime,
    prompt_runtime,
    agent_runtime,
    manifest_loader,
    writer,
    models,
    paths,
)

__version__ = "0.1.0"
