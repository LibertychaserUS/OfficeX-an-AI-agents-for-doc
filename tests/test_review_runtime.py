from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from tools.report_scaffold_v3.cli import app
from tools.report_scaffold_v3.review_runtime import build_review_ledger, extract_anchors_from_review_ledger

from .officex_exec_fixtures import create_officex_exec_fixture


def _write_manual_review_input(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _paragraph_exact_review_input(*, review_id: str = "manual-review-exact") -> dict:
    return {
        "review_id": review_id,
        "target_document_id": "candidate",
        "generated_by": "manual-review",
        "findings": [
            {
                "issue_id": "OX-001",
                "title": "Business model heading requires review",
                "issue_kind": "content_revision",
                "severity": "medium",
                "status": "open",
                "review_comment": "Check the heading anchor.",
                "anchor_rule": {
                    "anchor_rule_type": "paragraph_text",
                    "anchor_role": "business_model_heading",
                    "block_kind": "heading",
                    "match_mode": "exact",
                    "needle": "Business Model Analysis",
                },
            }
        ],
    }


def _paragraph_prefix_review_input(*, review_id: str = "manual-review-prefix") -> dict:
    return {
        "review_id": review_id,
        "target_document_id": "candidate",
        "generated_by": "manual-review",
        "findings": [
            {
                "issue_id": "OX-002",
                "title": "Traceability intro paragraph",
                "issue_kind": "content_revision",
                "severity": "medium",
                "status": "open",
                "review_comment": "Find the traceability introduction paragraph.",
                "anchor_rule": {
                    "anchor_rule_type": "paragraph_text",
                    "anchor_role": "traceability_intro",
                    "block_kind": "paragraph",
                    "match_mode": "prefix",
                    "needle": "To provide a structured assessment",
                },
            }
        ],
    }


def _table_cell_review_input(*, review_id: str = "manual-review-table") -> dict:
    return {
        "review_id": review_id,
        "target_document_id": "candidate",
        "generated_by": "manual-review",
        "findings": [
            {
                "issue_id": "OX-003",
                "title": "FR-07 evidence cell",
                "issue_kind": "content_revision",
                "severity": "low",
                "status": "open",
                "review_comment": "Find the evidence cell for FR-07.",
                "anchor_rule": {
                    "anchor_rule_type": "table_cell",
                    "anchor_role": "fr07_evidence_cell",
                    "header_values": ["FR ID", "Requirement", "Status", "Evidence", "Notes"],
                    "row_key": "FR-07",
                    "row_key_column": 0,
                    "target_column": 3,
                },
            }
        ],
    }


def test_build_review_ledger_compiles_valid_manual_review_json(tmp_path: Path):
    review_input_path = _write_manual_review_input(
        tmp_path / "review_input.json",
        _paragraph_exact_review_input(),
    )

    ledger, output_path = build_review_ledger(review_input_path=review_input_path)

    assert ledger.review_id == "manual-review-exact"
    assert ledger.findings[0].anchor_rule.anchor_rule_type == "paragraph_text"
    assert output_path.exists()


def test_build_review_ledger_rejects_invalid_manual_review_json_shape(tmp_path: Path):
    review_input_path = _write_manual_review_input(tmp_path / "invalid_review.json", {"review_id": "bad"})

    with pytest.raises(ValueError, match="Invalid OfficeXManualReviewInput schema"):
        build_review_ledger(review_input_path=review_input_path)


def test_extract_anchors_from_review_ledger_supports_paragraph_exact(tmp_path: Path):
    fixture = create_officex_exec_fixture(tmp_path)
    review_input_path = _write_manual_review_input(
        tmp_path / "review_exact.json",
        _paragraph_exact_review_input(),
    )
    _ledger, ledger_path = build_review_ledger(review_input_path=review_input_path)

    report = extract_anchors_from_review_ledger(
        candidate_path=fixture["candidate_path"],
        review_ledger_path=ledger_path,
    )

    payload = json.loads(report.anchor_snapshot_path.read_text(encoding="utf-8"))
    assert report.finding_count == 0
    assert payload["anchors"][0]["uniqueness_status"] == "unique"
    assert payload["anchors"][0]["block_kind"] == "heading"


def test_extract_anchors_from_review_ledger_supports_paragraph_prefix(tmp_path: Path):
    fixture = create_officex_exec_fixture(tmp_path)
    review_input_path = _write_manual_review_input(
        tmp_path / "review_prefix.json",
        _paragraph_prefix_review_input(),
    )
    _ledger, ledger_path = build_review_ledger(review_input_path=review_input_path)

    report = extract_anchors_from_review_ledger(
        candidate_path=fixture["candidate_path"],
        review_ledger_path=ledger_path,
    )

    payload = json.loads(report.anchor_snapshot_path.read_text(encoding="utf-8"))
    assert report.finding_count == 0
    assert payload["anchors"][0]["uniqueness_status"] == "unique"
    assert payload["anchors"][0]["block_kind"] == "paragraph"


def test_extract_anchors_from_review_ledger_supports_table_cell(tmp_path: Path):
    fixture = create_officex_exec_fixture(tmp_path)
    review_input_path = _write_manual_review_input(
        tmp_path / "review_table.json",
        _table_cell_review_input(),
    )
    _ledger, ledger_path = build_review_ledger(review_input_path=review_input_path)

    report = extract_anchors_from_review_ledger(
        candidate_path=fixture["candidate_path"],
        review_ledger_path=ledger_path,
    )

    payload = json.loads(report.anchor_snapshot_path.read_text(encoding="utf-8"))
    assert report.finding_count == 0
    assert payload["anchors"][0]["uniqueness_status"] == "unique"
    assert payload["anchors"][0]["block_kind"] == "table_cell"


def test_extract_anchors_from_review_ledger_rejects_missing_anchor_match(tmp_path: Path):
    fixture = create_officex_exec_fixture(tmp_path)
    review_input = _paragraph_exact_review_input(review_id="missing-anchor-review")
    review_input["findings"][0]["anchor_rule"]["needle"] = "Missing Heading Text"
    review_input_path = _write_manual_review_input(tmp_path / "review_missing.json", review_input)
    _ledger, ledger_path = build_review_ledger(review_input_path=review_input_path)

    report = extract_anchors_from_review_ledger(
        candidate_path=fixture["candidate_path"],
        review_ledger_path=ledger_path,
    )

    assert report.finding_count == 1
    payload = json.loads(report.anchor_snapshot_path.read_text(encoding="utf-8"))
    assert payload["anchors"][0]["uniqueness_status"] == "missing"


def test_extract_anchors_from_review_ledger_rejects_non_unique_anchor_match(tmp_path: Path):
    fixture = create_officex_exec_fixture(tmp_path, duplicate_business_model=True)
    review_input_path = _write_manual_review_input(
        tmp_path / "review_non_unique.json",
        _paragraph_exact_review_input(review_id="non-unique-review"),
    )
    _ledger, ledger_path = build_review_ledger(review_input_path=review_input_path)

    report = extract_anchors_from_review_ledger(
        candidate_path=fixture["candidate_path"],
        review_ledger_path=ledger_path,
    )

    assert report.finding_count == 1
    payload = json.loads(report.anchor_snapshot_path.read_text(encoding="utf-8"))
    assert payload["anchors"][0]["uniqueness_status"] == "non_unique"


def test_build_review_ledger_rejects_unsupported_anchor_rule_type(tmp_path: Path):
    review_input = _paragraph_exact_review_input(review_id="unsupported-rule-review")
    review_input["findings"][0]["anchor_rule"]["anchor_rule_type"] = "unsupported_kind"
    review_input_path = _write_manual_review_input(tmp_path / "review_unsupported.json", review_input)

    with pytest.raises(ValueError, match="Invalid OfficeXManualReviewInput schema"):
        build_review_ledger(review_input_path=review_input_path)


def test_officex_task_build_review_ledger_as_json_outputs_normalized_ledger(tmp_path: Path):
    runner = CliRunner()
    review_input_path = _write_manual_review_input(
        tmp_path / "cli_review_input.json",
        _paragraph_exact_review_input(review_id="cli-review-ledger"),
    )

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "build-review-ledger",
            "--review-findings",
            str(review_input_path),
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["review_id"] == "cli-review-ledger"
    assert payload["schema_version"] == 1


def test_officex_task_extract_anchors_as_json_outputs_report(tmp_path: Path):
    runner = CliRunner()
    fixture = create_officex_exec_fixture(tmp_path)
    review_input_path = _write_manual_review_input(
        tmp_path / "cli_extract_review.json",
        _paragraph_prefix_review_input(review_id="cli-extract-review"),
    )
    ledger_output = tmp_path / "cli_extract_review_ledger.json"
    build_result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "build-review-ledger",
            "--review-findings",
            str(review_input_path),
            "--output-path",
            str(ledger_output),
        ],
    )
    assert build_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "extract-anchors",
            "--candidate-docx",
            str(fixture["candidate_path"]),
            "--review-ledger",
            str(ledger_output),
            "--as-json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["review_id"] == "cli-extract-review"
    assert payload["anchor_count"] == 1
    assert Path(payload["anchor_snapshot_path"]).exists()


def test_officex_task_build_review_ledger_rejects_invalid_review_json(tmp_path: Path):
    runner = CliRunner()
    invalid_path = _write_manual_review_input(tmp_path / "invalid_cli_review.json", {"review_id": "bad"})

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "build-review-ledger",
            "--review-findings",
            str(invalid_path),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid OfficeXManualReviewInput schema" in result.stdout


def test_officex_task_extract_anchors_rejects_missing_candidate(tmp_path: Path):
    runner = CliRunner()
    review_input_path = _write_manual_review_input(
        tmp_path / "missing_candidate_review.json",
        _paragraph_exact_review_input(review_id="missing-candidate-review"),
    )
    _ledger, ledger_path = build_review_ledger(review_input_path=review_input_path)

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "extract-anchors",
            "--candidate-docx",
            str(tmp_path / "missing_candidate.docx"),
            "--review-ledger",
            str(ledger_path),
        ],
    )

    assert result.exit_code == 1
    assert "File not found" in result.stdout


def test_officex_task_extract_anchors_rejects_missing_review_ledger(tmp_path: Path):
    runner = CliRunner()
    fixture = create_officex_exec_fixture(tmp_path)

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "extract-anchors",
            "--candidate-docx",
            str(fixture["candidate_path"]),
            "--review-ledger",
            str(tmp_path / "missing_review_ledger.json"),
        ],
    )

    assert result.exit_code == 1
    assert "File not found" in result.stdout


def test_officex_task_extract_anchors_rejects_non_unique_anchor_resolution(tmp_path: Path):
    runner = CliRunner()
    fixture = create_officex_exec_fixture(tmp_path, duplicate_business_model=True)
    review_input_path = _write_manual_review_input(
        tmp_path / "cli_non_unique_review.json",
        _paragraph_exact_review_input(review_id="cli-non-unique-review"),
    )
    _ledger, ledger_path = build_review_ledger(review_input_path=review_input_path)

    result = runner.invoke(
        app,
        [
            "officex",
            "task",
            "extract-anchors",
            "--candidate-docx",
            str(fixture["candidate_path"]),
            "--review-ledger",
            str(ledger_path),
            "--as-json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["finding_count"] == 1
