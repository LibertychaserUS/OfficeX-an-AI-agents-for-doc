# CURRENT_STATE

## Platform Status

- Product identity: `Document Operations System`
- Active app codename: `OfficeX`
- Internal compatibility package: `tools.report_scaffold_v3`
- Current phase: `docx` MVP runtime-surface implementation
- Current runtime posture: fresh platform-local `.venv` rebuilt on Python 3.11
  and healthy
- Current research posture: external agent-cli reference corpus established for benchmark-driven redesign
- Current document-runtime posture: official `docx`/editor reference corpus established for OOXML, editor, and workspace comparison
- Current foundation posture: domain, prompt, memory, provider, desktop-runtime,
  and release-baseline contracts are now defined as active blueprints
- Current implementation posture: first OfficeX runtime CLI layer exists with
  workspace, sandbox, task, provider, prompt, agent, and trace command families
- Current prompt posture: OfficeX cognition and role-prompt composition now
  exist as callable runtime code
- Current agent posture: machine-readable agent catalog now exists as part of
  the active runtime baseline
- Current provider posture: provider baseline catalog and provider inspection
  commands now exist as callable runtime code
- Current provider-envelope posture: dry-run provider request envelopes can now
  be assembled from provider catalogs, role prompts, and runtime task packets
- Current patch-bridge posture: OfficeX patch bundles are being moved onto a
  native OfficeX execution core for bounded paragraph-level `docx` mutation
- Current review-prep posture: structured manual review JSON can now be
  normalized into an OfficeX review ledger and resolved into a live anchor
  snapshot
- Current development-workflow posture: a dedicated development-governance
  layer now exists under `docs/development` for development memory, telemetry,
  and cross-model review without redefining product runtime authority
- Current app-entry posture: a real `officex` console entry now exists and can
  route to `doctor`, `render-boundary`, runtime commands, or the desktop shell
- Current desktop-shell posture: an Electron+Bun macOS app scaffold now exists
  under `desktop/` as an intake-first three-column OfficeX workbench with
  preload IPC, machine-local workspace/thread state, confirmation-card intake,
  and in-shell utility actions for `doctor`, `render-boundary`, and one
  controlled `docx` run
- Current doctor posture: `officex doctor` now performs package, Bun, desktop,
  Word, workspace, sandbox, provider, and smoke-run checks, and now persists
  machine-readable JSON/Markdown reports plus latest-report pointers under the
  machine-local OfficeX settings root
- Current render-boundary posture: `officex render-boundary` now emits a
  Word-first renderer environment report and scenario-based capability matrix,
  and now persists report artifacts plus fixture/benchmark paths for audit
- Current product-entry invocation posture: desktop actions now call
  `tools.report_scaffold_v3.product_entry` directly so product-facing commands
  no longer depend on the raw legacy CLI root
- Current desktop-hardening posture: product-entry exit codes, sidecar spawn
  failures, machine-local settings writes, renderer save-settings errors, and
  `open-path` validation are now hardened for the current desktop MVP
- Current desktop-startup posture: the Electron shell now resolves preload
  outputs correctly, records startup diagnostics under the machine-local
  OfficeX log root, and no longer collapses bridge or render failures into a
  blank background-only window
- Current desktop-execution-log posture: app-triggered actions now persist
  `execution.json`, `stdout.log`, and `stderr.log` artifacts under the
  machine-local OfficeX runtime log root
- Current external-review posture: CodeRabbit agent authentication is now live
  on this machine and review CLI execution has been validated against the
  active OfficeX repository
- Current runtime-cleanup posture: low-risk backend-runtime deduplication is
  underway and currently preserving all active OfficeX CLI/runtime contracts
- Current CLI-cleanup posture: OfficeX-facing patch command wording has been
  tightened while legacy top-level command families remain deferred for a
  separate hardening slice
- Current runtime-observability posture: `run_docx_mvp` now emits a lightweight
  run-event log beside the existing stage-history review
- Historical case context lives outside the active OfficeX repository and is
  not part of the current default runtime path
- Current sandbox posture: platform-owned document-edit sandbox root established for mutable session copies
- Current CLI-surface posture: `cli.py` slimmed from 1814 to ~1400 lines by
  extracting 26 render functions into `cli_render.py`; new `officex audit visual`
  command family added for visual QA
- Current validation posture: monolithic `validation.py` (823 lines) decomposed
  into `validation/` subpackage with focused modules for page_setup,
  style_contract, image_fit, and override_detection
- Current writer posture: `writer.py` now warns on unknown write-contract fields
  in paragraph_format and run_format instead of silently skipping them
- Current visual-audit posture: LibreOffice headless rendering pipeline
  (`visual_audit.py`) and deterministic Pillow-based page checks
  (`visual_audit_checks.py`) are now live; `officex audit visual` CLI command
  exposes rendering and visual QA as a first-class runtime action
- Current golden-path posture: end-to-end pipeline test now cross-validates
  generated docx through both structural verification (open docx, assert
  paragraphs/styles/headings/geometry) and visual verification (render PNG,
  check blank pages/aspect ratio); both must pass

## Current Priorities

- stabilize `OfficeX` docx-first MVP governance
- keep AI/program boundaries explicit for document generation and revision
- build visual-audit and review-anchor primitives before broader UI work
  (visual-audit rendering and deterministic checks now implemented;
  review-anchor primitives were established in earlier checkpoints)
- wire the new domain/prompt/memory/provider/runtime contracts into the first
  executable OfficeX implementation slice
- expand the first runtime CLI slice into richer task/workspace/provider flows
- build provider request assembly and adapter logic on top of the new provider
  catalog and callable prompt runtime
- stabilize the new patch-bundle bridge before broadening into layout repair,
  figures, or richer patch scopes
- connect OfficeX review-ledger prep to future patch-bundle drafting through
  the OfficeX execution core
- keep replacing legacy-heavy regression coverage with OfficeX-native runtime
  tests as the new review-ledger and patch-bundle flows mature
- benchmark Codex and Claude runtime patterns before deeper runtime rewrites
- maintain a clean active-path model for daily development
- preserve compatibility while preparing future package migration
- replace remaining active-path legacy references after the neutral OfficeX baseline cutover
- keep the default recovery chain focused on OfficeX governance, not archived case context
- keep development-workflow optimization additive and separate from product
  runtime contracts
- continue backend-runtime cleanup through small, test-protected refactors
  rather than broad rewrites
- defer legacy top-level CLI command-family cleanup to a separate public-surface
  hardening stage
- keep extending OfficeX-native runtime regression coverage with realistic
  length profiles before broadening visual benchmark coverage
- harden the first app MVP around product entry, machine-local settings,
  `doctor`, `render-boundary`, and one controlled app-triggered `docx` run
- keep the current Electron shell local-development only until explicit macOS
  signing, entitlements, and notarization boundaries are defined

## Known Blockers

- no provider credentials are configured in the current environment, so live
  provider dispatch remains unavailable even though dry-run envelopes and
  package-level checks pass

## Recent Verification

- Fresh environment created at `/Users/nihao/Documents/Playground/document-ops-system/.venv`
- `check-package`: pass
- active Python baseline set to `3.11`
- `.python-version` now tracks `3.11`
- `requirements.lock.txt` updated to keep `typer==0.23.2` compatible with the
  Python 3.11 runtime by raising `click` to `8.2.1`
- `pytest -q`: `168 passed`
- local wheel build: pass
- archived `.venv` remains historical and should not be used for active execution
- active blueprint, review-anchor protocol, visual-audit policy, editor decision,
  and issue registers were added for the current `docx` MVP
- official `docx`/editor reference repositories were cloned and indexed locally
- active default manifests were cut over from archived `GU2` inputs to the neutral
  `OfficeX` sample template and baseline
- active bootstrap, navigation, template contracts, and issue routing were
  narrowed so archived case material is no longer part of the default OfficeX
  recovery path
- sandbox and editor-compatibility blueprints were added for the `docx` MVP
- domain-agent registry, prompt-evolution protocol, memory/RAG policy,
  provider-adapter contract, desktop-runtime contract, and release-baseline
  policy were added and linked into the active governance path
- OfficeX cognition prompt layer was added and composed into role prompts
- first OfficeX runtime CLI commands were added:
  - `officex sandbox create`
  - `officex task run-docx-mvp`
- the docx MVP runtime path now writes sandbox manifests, task packets,
  candidate outputs, validation reports, candidate audits, and runtime stage
  history reports inside sandbox runs
- tests were aligned to the neutral OfficeX template profile and now pass
- prompt composition is now implemented in code via a provider-neutral prompt
  runtime module and exposed through:
  - `officex prompt show`
- provider catalog inspection is now implemented in code and exposed through:
  - `officex provider list`
  - `officex provider show`
- provider catalog is now machine-readable and tracked at:
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/provider_catalog.yml`
- workspace, task-inspection, agent-inspection, and trace-checkpoint runtime
  commands now exist:
  - `officex workspace init`
  - `officex task inspect`
  - `officex agent list`
  - `officex agent show`
  - `officex trace checkpoint`
- runtime CLI commands now expose machine-readable JSON for:
  - `officex sandbox create`
  - `officex task run-docx-mvp`
  - `officex task build-review-ledger`
  - `officex task extract-anchors`
  - `officex task apply-patch-bundle`
  - `officex prompt show`
  - `officex provider build-request`
- full runtime-surface smoke verification passed for:
  - `officex workspace init --as-json`
  - `officex prompt show --role orchestrator --as-json`
  - `officex agent list --as-json`
  - `officex agent show --agent patch_assembly_engineer --as-json`
  - `officex task run-docx-mvp --run-id cli-runtime-smoke --sandbox-root /tmp/officex-cli-smoke --as-json`
  - `officex task inspect --run-id cli-runtime-smoke --sandbox-root /tmp/officex-cli-smoke --as-json`
  - `officex trace checkpoint --trace-dir /tmp/officex-trace-smoke --as-json`
- provider request-envelope smoke verification passed for:
  - `officex task run-docx-mvp --run-id provider-envelope-smoke --sandbox-root /tmp/officex-provider-envelope-smoke --as-json`
  - `officex provider build-request --provider openai --role orchestrator --run-id provider-envelope-smoke --sandbox-root /tmp/officex-provider-envelope-smoke --config-field api_key=demo --config-field model_id=gpt-5.4 --response-contract-kind plan_object --as-json`
- OfficeX patch bridge validation passed for:
  - paragraph-level `replace_text`
  - paragraph-level `insert_paragraph`
  - paragraph-level `restyle_paragraph`
  - `officex task apply-patch-bundle --dry-run`
- OfficeX review-prep validation passed for:
  - structured manual review JSON -> OfficeX review ledger
  - paragraph exact anchor extraction
  - paragraph prefix anchor extraction
  - table-cell anchor extraction
  - `officex task build-review-ledger --as-json`
  - `officex task extract-anchors --as-json`
- agent catalog is now machine-readable and tracked at:
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/agent_catalog.yml`
- desktop shell local verification passed at:
  - `cd desktop && bun run check`
- editable product entry installation passed at:
  - `.venv/bin/pip install -e /Users/nihao/Documents/Playground/document-ops-system`
- new focused Python verification passed:
  - `60 passed`
- product-entry routing smoke passed through:
  - `.venv/bin/officex doctor --workspace-root /tmp/officex-console-workspace --sandbox-root /tmp/officex-console-sandboxes --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop --as-json`
- product-entry runtime passthrough smoke passed through:
  - `.venv/bin/officex runtime task inspect --help`
- product-entry render-boundary smoke passed through:
  - `.venv/bin/officex render-boundary --workspace-root /tmp/officex-app-workspace --sandbox-root /tmp/officex-app-sandboxes --as-json`
- desktop doctor smoke passed through:
  - `.venv/bin/python -m tools.report_scaffold_v3.cli officex doctor --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop --as-json`
- desktop render-boundary smoke passed through:
  - `.venv/bin/python -m tools.report_scaffold_v3.cli officex render-boundary --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --as-json`
- app-backed controlled docx run smoke passed through:
  - `.venv/bin/python -m tools.report_scaffold_v3.cli officex task run-docx-mvp --run-id app-mvp-demo --sandbox-root /tmp/officex-app-mvp-sandboxes --as-json`
- local doctor result currently warns only on missing provider credentials
- local trace indexing passed through:
  - `.venv/bin/python -m tools.report_scaffold_v3.cli index-trace`
- local render-boundary result currently reports:
  - pass on short replace-text and medium insert-paragraph scenarios
  - warning on long restyle and ultra-long replace-text scenarios
  - Word detected at `/Applications/Microsoft Word.app` with version `16.108`
- readiness hardening verification passed for:
  - latest `doctor` reports now persist to machine-local archived and latest
    JSON/Markdown paths
  - desktop bootstrap now stays on `doctor` until the latest matching doctor
    result passes core checks
  - desktop product actions now run through
    `python -m tools.report_scaffold_v3.product_entry ...`
- post-hardening focused verification passed for:
  - `./.venv/bin/pytest tests/test_product_entry.py tests/test_doctor_runtime.py tests/test_render_boundary_runtime.py tests/test_runtime_surface_cli.py -q` -> `28 passed`
  - `OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings ./.venv/bin/python -m tools.report_scaffold_v3.product_entry doctor --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop --as-json`
  - `OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings ./.venv/bin/python -m tools.report_scaffold_v3.product_entry render-boundary --workspace-root /tmp/officex-app-mvp-workspace --sandbox-root /tmp/officex-app-mvp-sandboxes --as-json`
  - `OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings ./.venv/bin/python -m tools.report_scaffold_v3.product_entry runtime task run-docx-mvp --run-id app-mvp-post-fix --sandbox-root /tmp/officex-app-mvp-sandboxes --approval-mode ask_every_conflict --as-json`
- sandboxed Codex verification currently requires `OFFICEX_SETTINGS_DIR` to be
  redirected into `/tmp/...` because this execution environment cannot write to
  `~/Library/Application Support/OfficeX`; the product target remains
  machine-local Application Support outside the sandbox
- real machine-local verification is now also confirmed outside the sandbox for:
  - `doctor` writing to `/Users/nihao/Library/Application Support/OfficeX`
  - `render-boundary` writing to `/Users/nihao/Library/Application Support/OfficeX`
- CodeRabbit CLI verification now also passed for:
  - `coderabbit auth login --agent`
  - `coderabbit review --agent -t uncommitted -c AGENTS.md -c PROJECT.md`
  - review completed with `21` findings
- latest desktop hardening verification passed for:
  - `./.venv/bin/pytest tests/test_product_entry.py -q` -> `7 passed`
  - `cd desktop && bun test` -> `15 pass`
  - `cd desktop && bun run check` -> pass
- empty-shell recovery verification passed for:
  - `cd desktop && ELECTRON_ENABLE_LOGGING=1 ELECTRON_ENABLE_STACK_DUMPING=1 bun run app`
  - real app inspection confirmed OfficeX home content renders instead of an
    empty shell
  - in-app `检查这台 Mac` execution completed and surfaced doctor plus
    execution-log artifacts
- intake-first workbench verification passed for:
  - `cd desktop && bun test src/tests/rendererMarkup.test.tsx src/tests/taskIntake.test.ts src/tests/workbenchStateStore.test.ts src/tests/workbenchBootstrap.test.ts src/tests/actionPlans.test.ts src/tests/settingsStore.test.ts src/tests/sidecar.test.ts` -> `35 pass`
  - `cd desktop && bun run typecheck`

## Trace State

- Local platform checkpoint baseline created: `CHECKPOINT_01`
- Local smoke verification completed after environment rebuild
- External agent-cli reference corpus recorded in `CHECKPOINT_03`
- `OfficeX` docx-first MVP blueprint and issue registers recorded in `CHECKPOINT_04`
- `docx` runtime reference corpus recorded in `CHECKPOINT_05`
- neutral `OfficeX` baseline manifests recorded in `CHECKPOINT_06`
- OfficeX sandbox/editor integration cutover recorded in `CHECKPOINT_07`
- OfficeX foundation contracts for domains, prompts, memory, providers, desktop
  runtime, and release baseline recorded in `CHECKPOINT_08`
- OfficeX runtime CLI bootstrap and cognition-layer introduction recorded in
  `CHECKPOINT_09`
- OfficeX callable prompt runtime and prompt inspection command recorded in
  `CHECKPOINT_10`
- OfficeX provider registry and provider inspection CLI recorded in
  `CHECKPOINT_11`
- OfficeX runtime CLI surface expansion and agent registry recorded in
  `CHECKPOINT_12`
- OfficeX dry-run provider request envelopes and runtime-first onboarding
  cleanup recorded in `CHECKPOINT_13`
- OfficeX patch-bundle bridge and runtime patch application surface recorded in
  `CHECKPOINT_14`
- OfficeX desktop empty-shell recovery and in-app doctor verification recorded
  in `CHECKPOINT_25`
- OfficeX review-ledger and runtime anchor-prep surface recorded in
  `CHECKPOINT_15`
- OfficeX Python 3.11 baseline uplift and environment rebuild recorded in
  `CHECKPOINT_16`
- development workflow optimization documents and routing recorded in
  `CHECKPOINT_17`
- backend runtime low-risk cleanup recorded in `CHECKPOINT_18`
- backend runtime boundary tightening recorded in `CHECKPOINT_19`
- runtime length-profile regression and event logging recorded in
  `CHECKPOINT_20`
- provider prompt compiler structure and CLI clarification recorded in
  `CHECKPOINT_21`
- first app MVP product entry, desktop shell, doctor, and render-boundary
  recorded in `CHECKPOINT_22`
- app MVP readiness hardening and report persistence recorded in
  `CHECKPOINT_23`
- real machine-local verification, CodeRabbit activation, and desktop shell
  hardening recorded in `CHECKPOINT_24`
- Historical legacy checkpoints remain outside the active OfficeX repository
- Platform trace indexes should be regenerated from the local trace root only
- Claude Code session: backend generation chain slimmed, validation decomposed,
  writer hardened, golden-path end-to-end test added, visual audit pipeline
  (LibreOffice headless → PNG → deterministic checks) implemented, `officex
  audit visual` CLI command added — recorded in `CHECKPOINT_27`
