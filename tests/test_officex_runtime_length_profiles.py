from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from docx import Document
from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.officex_runtime import run_docx_mvp
from tools.report_scaffold_v3.paths import (
    DEFAULT_BASELINE_MANIFEST,
    DEFAULT_WRITE_CONTRACT_MANIFEST,
)


def _paragraph_text(profile_id: str, section_index: int, paragraph_index: int, repeat: int) -> str:
    seed = (
        f"OfficeX {profile_id} runtime paragraph {section_index}.{paragraph_index} "
        "verifies deterministic OOXML mutation, validation, audit stability, "
        "and contract-preserving backend behavior under sustained document load."
    )
    return " ".join(seed for _ in range(repeat))


def _build_source_payload(
    *,
    profile_id: str,
    section_count: int,
    paragraphs_per_section: int,
    sentence_repeat: int,
) -> dict:
    blocks: list[dict] = [
        {
            "kind": "paragraph",
            "role": "heading_1",
            "text": f"OfficeX {profile_id.title()} Runtime Length Test",
        }
    ]

    for section_index in range(1, section_count + 1):
        blocks.append(
            {
                "kind": "paragraph",
                "role": "heading_2",
                "text": f"Section {section_index} - {profile_id.title()} Coverage",
            }
        )
        for paragraph_index in range(1, paragraphs_per_section + 1):
            blocks.append(
                {
                    "kind": "paragraph",
                    "role": "indented_body" if paragraph_index % 3 == 0 else "body",
                    "text": _paragraph_text(
                        profile_id,
                        section_index,
                        paragraph_index,
                        sentence_repeat,
                    ),
                }
            )

    blocks.extend(
        [
            {
                "kind": "paragraph",
                "role": "heading_2",
                "text": "Appendix - Platform Placeholder",
            },
            {
                "kind": "paragraph",
                "role": "body",
                "text": (
                    "This appendix placeholder keeps the OfficeX runtime length "
                    "profile aligned with the current candidate-audit structure."
                ),
            },
        ]
    )
    return {
        "schema_version": 1,
        "document_id": f"officex-{profile_id}-runtime-length",
        "output_name": f"officex_{profile_id}_runtime_length.docx",
        "blocks": blocks,
    }


def _write_build_source(path: Path, payload: dict) -> Path:
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def _non_empty_paragraphs(docx_path: Path) -> list:
    document = Document(str(docx_path))
    return [paragraph for paragraph in document.paragraphs if paragraph.text.strip()]


def _assert_runtime_report_is_clean(report, *, expected_paragraph_count: int) -> None:
    assert report.candidate_error_count == 0
    assert report.candidate_warning_count == 0
    assert report.validation_error_count == 0
    assert report.validation_warning_count == 0
    assert report.candidate_docx.exists()
    assert report.stage_history_review_path.exists()
    assert (report.stage_history_review_path.parent / "run_event_log.json").exists()

    non_empty = _non_empty_paragraphs(report.candidate_docx)
    assert len(non_empty) == expected_paragraph_count
    assert non_empty[0].style.name == "Heading 1"
    assert non_empty[-2].text == "Appendix - Platform Placeholder"


@pytest.mark.parametrize(
    ("profile_id", "section_count", "paragraphs_per_section", "sentence_repeat"),
    [
        ("short", 2, 2, 1),
        ("medium", 4, 5, 2),
        ("long", 10, 8, 3),
        ("ultra_long", 18, 14, 4),
    ],
)
def test_officex_runtime_length_profiles(
    tmp_path: Path,
    profile_id: str,
    section_count: int,
    paragraphs_per_section: int,
    sentence_repeat: int,
) -> None:
    payload = _build_source_payload(
        profile_id=profile_id,
        section_count=section_count,
        paragraphs_per_section=paragraphs_per_section,
        sentence_repeat=sentence_repeat,
    )
    source_path = _write_build_source(tmp_path / f"{profile_id}_build.yml", payload)
    report = run_docx_mvp(
        run_id=f"{profile_id}-runtime-profile",
        sandbox_root=tmp_path / "sandboxes",
        source_path=source_path,
        baseline_manifest_path=DEFAULT_BASELINE_MANIFEST,
        write_contract_path=DEFAULT_WRITE_CONTRACT_MANIFEST,
        approval_mode="ask_every_conflict",
    )
    _assert_runtime_report_is_clean(report, expected_paragraph_count=len(payload["blocks"]))


def test_officex_task_run_docx_mvp_cli_accepts_long_profile_source(tmp_path: Path) -> None:
    runner = CliRunner()
    payload = _build_source_payload(
        profile_id="cli_long",
        section_count=12,
        paragraphs_per_section=10,
        sentence_repeat=3,
    )
    source_path = _write_build_source(tmp_path / "cli_long_build.yml", payload)

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "run-docx-mvp",
            "--run-id",
            "cli-long-runtime-profile",
            "--sandbox-root",
            str(tmp_path / "cli-sandboxes"),
            "--source",
            str(source_path),
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    run_summary = json.loads(result.stdout)
    candidate_docx = Path(run_summary["candidate_docx"])
    assert candidate_docx.exists()
    assert run_summary["candidate_error_count"] == 0
    assert run_summary["validation_error_count"] == 0
    assert len(_non_empty_paragraphs(candidate_docx)) == len(payload["blocks"])
