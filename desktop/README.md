# OfficeX Desktop Shell

Minimal Electron + Bun scaffold for the OfficeX desktop shell.

## What It Includes

- Electron main process with a hardened preload bridge
- React renderer with the product-facing home path `/让这台 Mac 准备就绪`
- bounded IPC for:
  - `doctor`
  - `render-boundary`
  - `run-docx-demo`
- command planning that can call the existing Python CLI when the local
  `.venv/bin/python` runtime is available
- stubbed fallback responses when the Python sidecar is not ready yet

## Local Commands

```bash
bun install
bun run dev
bun run test
bun run typecheck
bun run build
```

## Runtime Assumptions

- The desktop package lives under the active repo root.
- By default it looks for the Python runtime at `../.venv/bin/python`.
- You can override the repo root with `OFFICEX_REPO_ROOT=/absolute/path`.
- You can override the machine-local settings root with
  `OFFICEX_SETTINGS_DIR=/absolute/path`.
