---
doc_id: officex_claude_handoff_guide
layer: operational
authority: handoff
status: draft
owner: platform_governance
machine_source_of_truth: false
created_for: claude_development_handoff
---

# OfficeX Claude Handoff Guide

## Purpose

This document is a practical handoff guide for another coding agent, especially
Claude, to continue development in the active OfficeX repository.

It explains:

- what the project is
- where the current development progress stands
- where the important code paths live
- how document generation works
- how the desktop shell calls the Python runtime
- how to make changes without damaging the dirty worktree
- what the next sensible development slices are

This is not a new product contract. It is an operational teaching document.

## Active Project Boundary

The active project is:

```text
/Users/nihao/Documents/Playground/document-ops-system
```

Do not treat these as active implementation roots unless explicitly asked:

- `/Users/nihao/Documents/Playground/document-ops-system/references`
- `/Users/nihao/Documents/Playground/document-ops-system/docs/archive`
- `/Users/nihao/Documents/LegacyArchives/gu2-loopmart-outside-playground`

Those paths are reference, archive, or historical evidence. They can inform a
review, but they do not govern current development.

## Required First Reads

Before editing, read these files in this order:

1. `AGENTS.md`
2. `PROJECT.md`
3. `docs/ACTIVE_RULES_AND_PATHS.md`
4. `docs/ARCHITECTURE.md`
5. `trace/CURRENT_STATE.md`
6. `docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md`
7. The nearest implementation files for the task

The package name `tools.report_scaffold_v3` is a compatibility detail. The
product is `Document Operations System`; the current app codename is `OfficeX`.

## What The Product Is

OfficeX is a docx-first deliverable runtime.

The product direction is:

- formal deliverables should be built through explicit source layers
- AI can generate text, plans, findings, and code, but should not silently mutate
  Office document structure as final authority
- programmatic transforms own docx structure, styles, layout, numbering, assets,
  and export integrity
- mutable work should happen in sandboxes
- validation claims must state scope clearly: structural, semantic, layout, or
  mixed
- Microsoft Word compatibility is currently the phase-1 acceptance target

The active collaboration model is:

```text
platform truth + Office mirror
```

That means Word or an embedded editor can be a review surface, but the
authoritative mutation path should remain programmatic and auditable.

## Current Development Progress

The current phase is:

```text
docx MVP runtime-surface implementation
```

Implemented or partially implemented:

- Python runtime package under `tools/report_scaffold_v3`
- `officex` console entry through `tools.report_scaffold_v3.product_entry`
- runtime CLI families for workspace, sandbox, task, provider, prompt, agent,
  and trace
- deterministic docx generation through `writer.py`
- sandboxed docx MVP run through `officex_runtime.py`
- candidate audit, validation, font audit, outline audit, snippet audit, and
  trace indexing
- review ledger normalization and live anchor extraction
- OfficeX patch bundle bridge onto the native `officex_exec` executor
- provider catalog inspection and dry-run provider request envelope assembly
- Electron+Bun desktop shell under `desktop/`
- intake-first three-column workbench UI
- machine-local workspace/thread state
- task confirmation-card intake
- bounded utility actions for:
  - `doctor`
  - `render-boundary`
  - one controlled `docx` MVP run
- desktop IPC boundary, sidecar execution, artifact opening policy, and execution
  logs
- startup diagnostics under the machine-local OfficeX log root

Known unfinished or constrained areas:

- live provider dispatch is not available without provider credentials
- the desktop shell is a local-development MVP, not signed or distribution-ready
- embedded editor integration is still future-facing; do not claim full editor
  workbench support
- the confirmation-card workflow exists, but richer task transition and
  domain-agent fan-out are not complete
- visual audit and layout benchmark coverage should grow before broader
  document-production claims
- backend cleanup is underway but should be done in small, test-protected slices

The repository is currently dirty. A future agent must run:

```bash
git status --short
```

before changing anything, and must not revert changes it did not make.

## Main Repository Map

```text
AGENTS.md                         project-local working rules
PROJECT.md                        product charter and MVP boundary
README.md                         operator-facing overview and quick start
docs/                             active governance, architecture, roadmap, registers
docs/development/                 development-process notes and handoff docs
docs/blueprints/                  active product/runtime design blueprints
harnesses/                        playbooks for recurring task families
manifests/                        machine-readable contracts and catalogs
sources/                          managed input material and demo sources
tools/report_scaffold_v3/         Python runtime implementation
tests/                            Python tests
desktop/                          Electron+Bun OfficeX desktop shell
trace/                            local project state, checkpoints, replay notes
outputs/                          generated candidates, audits, published metadata
sandboxes/                        mutable document-editing sandboxes
```

Machine-local OfficeX app state is outside the repository:

```text
/Users/nihao/Library/Application Support/OfficeX
```

That directory can contain settings, doctor reports, desktop logs, and execution
logs. It is not product authority.

## Backend Document Generation Path

The real backend generation code is not `cli.py`. The CLI is mostly a command
surface.

The generation chain is:

```text
manifests + sources
  -> manifest_loader.py
  -> section_assembler.py / snippet_compiler.py
  -> writer.py
  -> officex_runtime.py
  -> candidate_audit.py + validation.py
  -> sandbox reports and output docx
```

Important files:

```text
tools/report_scaffold_v3/manifest_loader.py
tools/report_scaffold_v3/section_assembler.py
tools/report_scaffold_v3/snippet_compiler.py
tools/report_scaffold_v3/writer.py
tools/report_scaffold_v3/officex_runtime.py
tools/report_scaffold_v3/candidate_audit.py
tools/report_scaffold_v3/validation.py
```

The true docx writer is:

```text
tools/report_scaffold_v3/writer.py
```

Its core function is:

```python
build_word_candidate(...)
```

That function:

1. opens a template docx
2. optionally clears existing body content
3. parses paragraph and image blocks
4. applies write-contract roles
5. writes paragraphs, images, and captions
6. saves the output docx

The full OfficeX docx MVP run is:

```text
tools/report_scaffold_v3/officex_runtime.py
```

Its key functions are:

```python
create_docx_mvp_sandbox(...)
run_docx_mvp(...)
```

`run_docx_mvp(...)` does the complete sandboxed loop:

1. load baseline, build source, write contract, template profile, layout contract
2. create sandbox
3. copy the baseline/template docx into sandbox input
4. write a task packet
5. inspect the baseline
6. build candidate docx
7. write build summary
8. run candidate audit
9. inspect candidate OOXML and effective styles
10. run validation
11. write stage history, event log, and run summary

## Generation Inputs

Primary generation input files:

```text
sources/minimal_build.yml
sources/sections/demo/*.md
manifests/baseline.yml
manifests/sections.yml
manifests/figures.yml
manifests/snippets.yml
manifests/write_contract.yml
manifests/template_profile.yml
manifests/layout_contract.yml
```

Mental model:

- `baseline.yml` says what docx/template is authoritative for the current run
- `write_contract.yml` maps semantic roles to Word styles and formatting
- `template_profile.yml` describes expected template/page/style behavior
- `layout_contract.yml` describes layout rules and override policies
- `sources/minimal_build.yml` is an already-assembled build source
- `sections.yml`, `figures.yml`, and `snippets.yml` are higher-level managed
  inputs that can be assembled into a build source

## Desktop Runtime Path

The desktop shell lives in:

```text
desktop/
```

The important flow is:

```text
React renderer
  -> preload bridge
  -> Electron main IPC handler
  -> actionPlans.ts
  -> sidecar.ts
  -> python -m tools.report_scaffold_v3.product_entry
  -> OfficeX Python CLI/runtime
```

Important desktop files:

```text
desktop/src/renderer/src/App.tsx
desktop/src/renderer/src/components/WorkbenchSidebar.tsx
desktop/src/renderer/src/components/WorkbenchCenter.tsx
desktop/src/renderer/src/components/ChatDock.tsx
desktop/src/renderer/src/components/RunArtifactsPanel.tsx
desktop/src/preload/index.ts
desktop/src/main/index.ts
desktop/src/main/actionPlans.ts
desktop/src/main/sidecar.ts
desktop/src/main/settingsStore.ts
desktop/src/main/workbenchStateStore.ts
desktop/src/main/taskIntake.ts
desktop/src/main/openPathPolicy.ts
desktop/src/shared/types.ts
```

The renderer should not call arbitrary shell commands. It should use the preload
API and bounded IPC actions.

The current allowed desktop action ids are:

```text
doctor
render-boundary
run-docx-demo
```

Do not expand this into generic shell execution.

## CLI And Product Entry

Console entry points are defined in `pyproject.toml`:

```text
officex = tools.report_scaffold_v3.product_entry:entrypoint
document-ops-system = tools.report_scaffold_v3.cli:main
report-scaffold-v3 = tools.report_scaffold_v3.cli:main
```

Current preferred product-facing command:

```bash
.venv/bin/officex doctor --workspace-root /tmp/officex-workspaces --sandbox-root /tmp/officex-sandboxes --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop --as-json
```

Compatibility root commands such as `build-word`, `validate-word`, and
`run-section-pipeline` still exist, but they should be treated as deterministic
compatibility primitives, not the future public surface.

## How To Start A Development Session

Use this sequence:

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git status --short
sed -n '1,220p' AGENTS.md
sed -n '1,220p' PROJECT.md
sed -n '1,260p' trace/CURRENT_STATE.md
```

Then identify the task family:

- ingestion
- generation
- revision
- audit
- release
- desktop shell
- runtime/provider/prompt
- trace/governance

Choose the nearest harness if the work touches a recurring document task:

```text
harnesses/document_ingestion.md
harnesses/document_generation.md
harnesses/document_revision.md
harnesses/template_alignment.md
harnesses/asset_binding.md
harnesses/compliance_review.md
harnesses/render_audit.md
harnesses/publication_release.md
```

State the expected validation scope before claiming success:

- structural
- semantic
- layout
- mixed

## Safe Editing Rules For Claude

The worktree is dirty, so use these rules:

- never run `git reset --hard`
- never revert files unless the user explicitly asks
- never delete archive/reference material as cleanup without explicit approval
- read a file before editing it
- make one bounded change at a time
- keep backend cleanup separate from desktop UI work
- keep product docs separate from machine-local state
- do not move large module groups in one patch
- prefer compatibility shims during refactors
- run targeted tests for the exact files touched
- record blockers precisely instead of claiming broad success

If a file already has unrelated changes, preserve them. If the task requires
editing the same file, patch only the local region needed for the task.

## Recommended Next Development Slices

### 1. Backend Generation Code Map

Goal: make backend generation easier to navigate without moving code yet.

Suggested work:

- keep `writer.py`, `section_assembler.py`, and `officex_runtime.py` documented
  as the current generation core
- add tests only if behavior is unclear
- avoid moving files while the tree is dirty

Validation:

```bash
.venv/bin/pytest tests/test_writer.py tests/test_section_assembler.py tests/test_officex_runtime_cli.py -q
```

### 2. CLI Surface Cleanup

Goal: reduce `cli.py` density without changing behavior.

Why: `cli.py` currently contains command declarations plus many render helper
functions. It is easy for future agents to mistake it for the generation core.

Safe path:

1. extract render helpers into a dedicated module
2. keep command names and options stable
3. run runtime CLI tests
4. only then consider moving command implementations

Validation:

```bash
.venv/bin/pytest tests/test_cli.py tests/test_runtime_surface_cli.py tests/test_product_entry.py -q
```

### 3. Generation Package Refactor

Goal: eventually group generation code under a clearer package.

Target shape:

```text
tools/report_scaffold_v3/generation/
  writer.py
  section_assembler.py
  snippet_compiler.py
  section_pipeline.py
```

Safe migration pattern:

1. create the new package
2. move one module
3. leave old import path as a compatibility wrapper
4. update tests for the new path only after the wrapper passes
5. repeat

Do not do a broad import rewrite until tests are green after each step.

### 4. Runtime Orchestration Split

Goal: make `officex_runtime.py` easier to extend.

Possible future split:

```text
runtime/sandbox.py
runtime/docx_mvp_run.py
runtime/reports.py
runtime/task_packets.py
```

Do this after generation code is stable. `run_docx_mvp(...)` is a central
contract, so keep it callable during migration.

### 5. Provider Adapter Implementation

Goal: move beyond dry-run provider envelopes.

Current state:

- provider catalog exists
- provider prompt binding exists
- provider request envelope exists
- live dispatch is blocked by missing credentials and adapter implementation

Safe path:

1. keep provider credentials out of renderer state
2. add adapter behind an explicit provider runtime boundary
3. start with dry-run and mocked tests
4. add live smoke only when credentials are intentionally configured

### 6. Desktop Task Workflow

Goal: connect intake and confirmation more deeply to real task execution.

Current state:

- intake-first shell exists
- workspace/thread state exists
- confirmation-card generation exists
- utility actions are wired

Next likely work:

- make confirmation choices explicit and persisted
- route confirmed task type to the appropriate bounded runtime action
- avoid inert UI controls
- keep inactive workspaces overview-only unless navigation is wired

Validation:

```bash
cd desktop
bun test
bun run typecheck
```

### 7. Visual And Render Audit

Goal: strengthen layout proof.

Current state:

- `validate-word` covers structural/layout-contract checks
- `render-boundary` measures Word-first capability scenarios
- visual audit policy exists, but broader visual benchmark coverage is still
  future work

Do not claim visual correctness from structural checks alone.

## Useful Validation Commands

Python package and focused tests:

```bash
.venv/bin/python -m tools.report_scaffold_v3.cli check-package
.venv/bin/pytest tests/test_writer.py tests/test_section_assembler.py -q
.venv/bin/pytest tests/test_product_entry.py tests/test_doctor_runtime.py tests/test_render_boundary_runtime.py tests/test_runtime_surface_cli.py -q
```

OfficeX runtime smoke with sandboxed machine-local state:

```bash
OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings \
  .venv/bin/python -m tools.report_scaffold_v3.product_entry doctor \
  --workspace-root /tmp/officex-app-workspace \
  --sandbox-root /tmp/officex-app-sandboxes \
  --desktop-shell-dir /Users/nihao/Documents/Playground/document-ops-system/desktop \
  --as-json

OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings \
  .venv/bin/python -m tools.report_scaffold_v3.product_entry render-boundary \
  --workspace-root /tmp/officex-app-workspace \
  --sandbox-root /tmp/officex-app-sandboxes \
  --as-json

OFFICEX_SETTINGS_DIR=/tmp/officex-app-settings \
  .venv/bin/python -m tools.report_scaffold_v3.product_entry runtime task run-docx-mvp \
  --run-id app-mvp-smoke \
  --sandbox-root /tmp/officex-app-sandboxes \
  --approval-mode ask_every_conflict \
  --as-json
```

Desktop checks:

```bash
cd /Users/nihao/Documents/Playground/document-ops-system/desktop
bun test
bun run typecheck
bun run check
```

Desktop local app launch:

```bash
cd /Users/nihao/Documents/Playground/document-ops-system/desktop
ELECTRON_ENABLE_LOGGING=1 ELECTRON_ENABLE_STACK_DUMPING=1 bun run app
```

If running from a sandboxed agent environment, redirect `OFFICEX_SETTINGS_DIR`
to `/tmp/...` unless machine-local Application Support access is intentionally
approved.

## Common Misreadings To Avoid

Do not assume:

- `tools.report_scaffold_v3` means the project is still only a report scaffold
- `cli.py` is the generation engine
- a successful structural validation proves visual correctness
- `references/` is active product code
- archived GU2 material governs current OfficeX behavior
- desktop shell local launch equals signed macOS distribution readiness
- provider envelope generation equals live provider dispatch
- Word/editor manual edits are the source of truth

Correct interpretation:

- OfficeX is the active app/runtime layer
- `writer.py` writes docx candidates
- `officex_runtime.py` orchestrates the sandboxed docx MVP run
- `desktop/` is a local Electron MVP shell
- `manifests/` and `sources/` define managed input contracts
- `trace/` records active local project state

## Current Best Answer To "Where Are We?"

The project has moved past a pure scaffold. It now has a working docx-first
runtime skeleton, a local Electron desktop shell, bounded desktop actions, and a
deterministic backend path that can create a sandbox, generate a docx candidate,
audit it, validate it, and write traceable reports.

It is not yet a finished product. The next work should focus on making the
backend easier to maintain, keeping the desktop workflow honest and wired, and
adding real provider/editor/visual-audit depth without breaking the current
docx MVP contracts.

## Suggested First Claude Task

The safest first task for Claude is:

```text
Read this handoff, AGENTS.md, PROJECT.md, ACTIVE_RULES_AND_PATHS.md, and
trace/CURRENT_STATE.md. Then produce a no-edit implementation plan for either
backend generation cleanup or desktop workflow continuation, including exact
files, test commands, and risks.
```

After that, choose one small slice and implement it with targeted tests.
