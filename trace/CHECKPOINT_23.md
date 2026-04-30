# CHECKPOINT_23

date: 2026-04-21

## Title

OfficeX app MVP readiness hardening and report persistence

## Summary

- `doctor` and `render-boundary` reports are now persisted as stable artifacts
  under the machine-local OfficeX settings root with:
  - per-run archived JSON and Markdown reports
  - `latest.json`
  - `latest.md`
- the desktop shell no longer treats Python detection alone as readiness:
  readiness now depends on the latest matching `doctor` result for the current
  workspace and sandbox, plus current Word visibility
- desktop product actions now run through
  `python -m tools.report_scaffold_v3.product_entry ...` instead of calling the
  raw legacy CLI root directly
- `tools.report_scaffold_v3.product_entry` now has a real `__main__` module
  entry so module-based execution works outside editable-script assumptions
- `render-boundary` now records:
  - source fixture directory
  - benchmark run root
  - persisted report paths
- the desktop renderer now refreshes bootstrap state after actions so the home
  screen reflects the latest `doctor` result without restarting the app

## Verification

- `./.venv/bin/pytest tests/test_product_entry.py tests/test_doctor_runtime.py tests/test_render_boundary_runtime.py tests/test_runtime_surface_cli.py -q` -> `28 passed`
- `cd desktop && bun run check` -> pass
- `OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings ./.venv/bin/python -m tools.report_scaffold_v3.product_entry doctor --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop --as-json` -> warning only for missing provider credentials, with persisted report paths
- `OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings ./.venv/bin/python -m tools.report_scaffold_v3.product_entry render-boundary --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --as-json` -> warning on long and ultra-long scenarios, with persisted report paths, fixture dir, and benchmark root
- `OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings ./.venv/bin/python -m tools.report_scaffold_v3.product_entry runtime task run-docx-mvp --run-id app-mvp-post-fix --sandbox-root /tmp/officex-app-mvp-sandboxes --approval-mode ask_every_conflict --as-json` -> pass

## Follow-up

- keep expanding `render-boundary` beyond length bands into richer structure
  and patch-risk scenarios
- add UI-level tests for bootstrap refresh and latest-report affordances
- decide whether machine-local report storage should later support explicit
  cleanup and retention policy controls
- preserve the current split between machine-local diagnostics and product
  authority files
