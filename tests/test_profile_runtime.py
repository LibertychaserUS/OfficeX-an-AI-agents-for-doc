from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.report_scaffold_v3 import profile_runtime
from tools.report_scaffold_v3.models import (
    LayoutContractManifest,
    TemplateProfileManifest,
    WriteContractManifest,
)

MODELS = {
    "template_profile.yml": TemplateProfileManifest,
    "layout_contract.yml": LayoutContractManifest,
    "write_contract.yml": WriteContractManifest,
}


def _load_profile_dir(profile_dir: Path) -> None:
    for name, model_type in MODELS.items():
        raw = yaml.safe_load((profile_dir / name).read_text(encoding="utf-8")) or {}
        model_type.model_validate(raw)


@pytest.mark.parametrize(
    "profile_dir",
    sorted(p for p in profile_runtime.PROFILES_DIR.iterdir() if p.is_dir()),
    ids=lambda p: p.name,
)
def test_shipped_profiles_load_with_runtime_models(profile_dir: Path):
    # `officex profile use` copies these files over the active manifests, so each one
    # must load with the same models the runtime uses.
    _load_profile_dir(profile_dir)


def test_created_profile_loads_with_runtime_models(monkeypatch, tmp_path):
    monkeypatch.setattr(profile_runtime, "PROFILES_DIR", tmp_path)

    result = profile_runtime.create_profile("b5_test", page_width_pt=515.9, page_height_pt=728.5)

    _load_profile_dir(Path(result["path"]))


def test_run_docx_mvp_reports_role_mismatch_without_traceback(tmp_path):
    from typer.testing import CliRunner

    from tools.report_scaffold_v3.cli import app

    letter_contract = profile_runtime.PROFILES_DIR / "letter_business" / "write_contract.yml"
    result = CliRunner().invoke(
        app,
        [
            "officex", "task", "run-docx-mvp",
            "--sandbox-root", str(tmp_path),
            "--write-contract", str(letter_contract),
        ],
    )

    output = " ".join(result.stdout.split())  # rich wraps long lines at the terminal width
    assert result.exit_code == 1
    assert "Unknown paragraph role `indented_body`" in output
    assert "officex profile use a4_academic" in output
    assert not isinstance(result.exception, ValueError)
