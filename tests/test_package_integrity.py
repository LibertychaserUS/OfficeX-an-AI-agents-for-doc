from pathlib import Path

from tools.report_scaffold_v3.package_contract import (
    CORE_MODULES,
    MIN_SUPPORTED_PYTHON,
    collect_package_integrity_issues,
)


def test_core_module_contract_covers_validation_engine():
    specs = {spec.file_name: spec.import_name for spec in CORE_MODULES}
    assert specs["candidate_audit.py"] == "tools.report_scaffold_v3.candidate_audit"
    assert specs["font_audit.py"] == "tools.report_scaffold_v3.font_audit"
    assert specs["ooxml_styles.py"] == "tools.report_scaffold_v3.ooxml_styles"
    assert specs["outline_audit.py"] == "tools.report_scaffold_v3.outline_audit"
    assert specs["publication.py"] == "tools.report_scaffold_v3.publication"
    assert specs["officex_exec/__init__.py"] == "tools.report_scaffold_v3.officex_exec"
    assert specs["officex_exec/common.py"] == "tools.report_scaffold_v3.officex_exec.common"
    assert specs["officex_exec/models.py"] == "tools.report_scaffold_v3.officex_exec.models"
    assert specs["officex_exec/anchor_extractor.py"] == "tools.report_scaffold_v3.officex_exec.anchor_extractor"
    assert specs["officex_exec/executor.py"] == "tools.report_scaffold_v3.officex_exec.executor"
    assert specs["patch_bridge_runtime.py"] == "tools.report_scaffold_v3.patch_bridge_runtime"
    assert specs["section_assembler.py"] == "tools.report_scaffold_v3.section_assembler"
    assert specs["section_pipeline.py"] == "tools.report_scaffold_v3.section_pipeline"
    assert specs["review_runtime.py"] == "tools.report_scaffold_v3.review_runtime"
    assert specs["snippet_audit.py"] == "tools.report_scaffold_v3.snippet_audit"
    assert specs["snippet_compiler.py"] == "tools.report_scaffold_v3.snippet_compiler"
    assert specs["trace_indexer.py"] == "tools.report_scaffold_v3.trace_indexer"
    assert specs["validation/__init__.py"] == "tools.report_scaffold_v3.validation"
    assert specs["writer.py"] == "tools.report_scaffold_v3.writer"


def test_required_core_module_files_exist_and_import_cleanly():
    issues = collect_package_integrity_issues()
    assert not issues


def test_package_contract_detects_missing_core_module_files(tmp_path: Path):
    fake_root = tmp_path / "report_scaffold_v3"
    fake_root.mkdir()
    (fake_root / "__init__.py").write_text('"""fake"""', encoding="utf-8")

    issues = collect_package_integrity_issues(package_root=fake_root, check_imports=False)

    missing_messages = [issue.message for issue in issues if issue.code == "missing-core-module-file"]
    assert missing_messages
    assert any("validation/__init__.py" in message for message in missing_messages)


def test_python_runtime_floor_is_python_311():
    assert MIN_SUPPORTED_PYTHON == (3, 11)
