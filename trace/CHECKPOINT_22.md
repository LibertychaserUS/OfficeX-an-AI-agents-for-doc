# CHECKPOINT_22

date: 2026-04-21

## Title

First OfficeX app MVP product entry, doctor, render-boundary, and desktop shell

## Summary

- `officex` is now a real product entry after editable install, routing the
  desktop shell, `doctor`, `render-boundary`, and `runtime ...` commands.
- The first Electron+Bun macOS desktop shell now exists under `desktop/` with
  a readiness-first home, hardened preload IPC, and bounded actions for:
  - `doctor`
  - `render-boundary`
  - `run-docx-demo`
- `officex doctor` now emits a structured machine-readiness report covering:
  - Python/package integrity
  - Bun availability
  - desktop-shell presence
  - Microsoft Word detection
  - workspace/sandbox writability
  - provider catalog readability
  - provider credential presence
  - one runtime smoke run
- `officex render-boundary` now emits a Word-first renderer report with:
  - short, medium, long, and ultra-long scenarios
  - a capability matrix
  - localization and patch-applicability confidence
  - explicit residual-risk notes
- The first app-backed controlled `docx` task loop is now verified end-to-end
  through the active OfficeX runtime surface.

## Verification

- `.venv/bin/python -m pytest -q` -> `168 passed`.
- `cd desktop && bun run check` -> pass.
- `.venv/bin/python -m tools.report_scaffold_v3.cli check-package` -> pass.
- `.venv/bin/pip install -e /Users/nihao/Documents/Playground/document-ops-system` -> pass.
- `.venv/bin/officex doctor --workspace-root /tmp/officex-entry-workspace --sandbox-root /tmp/officex-entry-sandboxes --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop --as-json` -> pass with warning only for missing provider credentials.
- `.venv/bin/python -m tools.report_scaffold_v3.cli officex doctor --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop --as-json` -> pass with warning only for missing provider credentials.
- `.venv/bin/python -m tools.report_scaffold_v3.cli officex render-boundary --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --as-json` -> pass with:
  - short replace-text: pass
  - medium insert-paragraph: pass
  - long restyle: warning
  - ultra-long replace-text: warning
- `.venv/bin/python -m tools.report_scaffold_v3.cli officex task run-docx-mvp --run-id app-mvp-demo --sandbox-root /tmp/officex-app-mvp-sandboxes --as-json` -> pass.
- targeted doctor edge-case test now also passes for:
  - desktop shell source present but Bun dependencies missing -> `warning`

## Follow-up

- Keep the first app MVP narrow around readiness, boundary evidence, and one
  controlled run before expanding into a full workbench.
- Define macOS bundle id, entitlements, hardened runtime, signing, and
  notarization posture before making distribution claims.
- Broaden render-boundary scenarios to cover richer structures and future
  desktop/editor integration work.
