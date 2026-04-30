# CHECKPOINT_25

date: 2026-04-21

## Title

OfficeX desktop empty-shell root-cause fix and real in-app doctor verification

## Summary

- the reported "empty shell" was traced to a real startup defect, not missing
  product content:
  - Electron created the window
  - renderer loaded styles
  - preload failed to load
  - `window.officex` was undefined
  - the renderer then crashed into a visually empty background-only state
- the root cause was two-part:
  - preload output had been emitted as CommonJS after the format fix
  - the main process still resolved the preload path incorrectly at first
- the desktop shell now hardens this path with:
  - explicit preload output format set to CommonJS in `electron.vite.config.ts`
  - preload-path resolution that checks `index.cjs`, `index.js`, and `index.mjs`
  - startup diagnostics persisted under the machine-local OfficeX log root
  - renderer-side bridge checks so missing preload no longer becomes a silent
    blank window
  - a renderer error boundary so uncaught render failures surface as visible
    product errors instead of an empty shell
- desktop action metadata and execution persistence were also completed so the
  current shell type-checks cleanly and action runs now retain execution logs

## Verification

- real Electron startup verification first reproduced the failure through:
  - `cd desktop && ELECTRON_ENABLE_LOGGING=1 ELECTRON_ENABLE_STACK_DUMPING=1 bun run app`
  - observed errors included:
    - `Unable to load preload script`
    - `Cannot use import statement outside a module`
    - later `ENOENT` on an incorrect preload path after the format change
- real Electron startup verification then passed after the fix through:
  - `cd desktop && ELECTRON_ENABLE_LOGGING=1 ELECTRON_ENABLE_STACK_DUMPING=1 bun run app`
  - confirmed:
    - preload path resolved to `desktop/out/preload/index.cjs`
    - no further `window.officex` bootstrap errors appeared
    - window URL loaded at `http://localhost:5173/`
- desktop UI verification passed through direct app inspection:
  - the OfficeX home screen rendered real content instead of a blank shell
  - the in-app `检查这台 Mac` action completed successfully
  - result artifacts were surfaced in-app, including:
    - `doctor_report.json`
    - `doctor_report.md`
    - `execution.json`
    - `stdout.log`
    - `stderr.log`
- desktop regression verification passed:
  - `cd desktop && bun run typecheck`
  - `cd desktop && bun test`
  - `cd desktop && bun run check`

## Follow-up

- the current dev shell still emits the standard Electron CSP warning and
  should later gain an explicit desktop CSP policy
- startup diagnostics now exist, but they should be folded into a broader
  operator-facing log and error-reporting model instead of remaining only a
  desktop bootstrap aid
- render-boundary and controlled docx runs should also be exercised from the
  app surface after the empty-shell recovery so the first full product loop is
  covered under the new logging path
