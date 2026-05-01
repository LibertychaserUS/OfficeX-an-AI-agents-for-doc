# CHECKPOINT_27

## Title

Backend generation chain hardening, visual audit pipeline, and golden-path cross-validation

## Summary

- Extracted 26 render functions from `cli.py` into `cli_render.py` (cli.py: 1814 → ~1400 lines)
- Decomposed monolithic `validation.py` (823 lines) into `validation/` subpackage with 5 focused modules: common, page_setup, style_contract, image_fit, override_detection
- Added unknown-field warnings to `writer.py` format application functions
- Created end-to-end golden-path test covering manifest → docx → audit → validation chain
- Implemented visual audit pipeline: LibreOffice headless docx→PDF→PNG rendering (`visual_audit.py`) + deterministic Pillow checks (`visual_audit_checks.py`)
- Added `officex audit visual` CLI command for standalone visual QA
- Golden-path test now cross-validates: structural checks + visual render checks must both pass
- Added `numpy` and `pymupdf` dependencies for visual audit
- LibreOffice 26.2.3.2 installed and verified on this machine

## Verification

- `pytest -q`: 179 passed
- `officex audit visual --candidate-docx ... --as-json`: renders and reports correctly
- `desktop/bun test`: 39 passed (unchanged from prior checkpoint)
- Golden path test runs both structural and visual validation in a single test

## Follow-up

- Provider adapter implementation (dry-run → live dispatch)
- Desktop task workflow continuation
- Render diff capability (compare two docx visually)
