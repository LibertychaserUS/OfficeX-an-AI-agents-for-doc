# Document Operations System

This repository contains a multi-agent document engineering platform for
ingestion, generation, revision, audit, release, and replayable trace.

It was incubated from a report-oriented scaffold, but it is now positioned as a
broader deliverable runtime.

The current internal codename for the app surface is:

- `OfficeX`

The current MVP focus is:

- `docx` only
- Microsoft Word-compatible output
- desktop-first human-in-the-loop workflow

## Compatibility Note

The product name is `Document Operations System`.

During this transition period, the internal Python package and CLI module path
remain:

- `tools.report_scaffold_v3`

That is a technical compatibility detail, not the product identity.

## Layout

- `docs/`: product governance, architecture, workflow, and roadmap
- `harnesses/`: reusable execution playbooks for recurring task families
- `manifests/`: contracts, catalogs, and managed configuration
- `prompts/`: local multi-agent prompt pack
- `sources/`: starter managed inputs and demo sources
- `tools/`: platform implementation
- `tests/`: automated verification
- `trace/`: local replay and status records for the platform itself
- `imports/`, `locks/`, `logs/`, `outputs/`: run-time platform workspaces

## Quick Start

Create a local environment if needed. The active OfficeX runtime baseline is
Python 3.11:

```bash
/opt/homebrew/bin/python3.11 -m venv .venv
.venv/bin/python --version
.venv/bin/pip install -r requirements.lock.txt
```

Primary smoke commands:

```bash
.venv/bin/python -m tools.report_scaffold_v3.cli check-package
.venv/bin/pytest -q
```

Useful OfficeX runtime commands:

```bash
.venv/bin/python -m tools.report_scaffold_v3.cli officex workspace init --workspace-id demo --workspace-root /tmp/officex-workspaces --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex sandbox create --run-id demo-run --sandbox-root /tmp/officex-sandboxes --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task run-docx-mvp --run-id demo-run --sandbox-root /tmp/officex-sandboxes --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task inspect --run-id demo-run --sandbox-root /tmp/officex-sandboxes --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task build-review-ledger --review-findings /tmp/officex-review-input.json --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task extract-anchors --candidate-docx /tmp/officex-sandboxes/demo-run/candidate/minimal_writer_demo.docx --review-ledger /tmp/officex-review-ledger.json --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task apply-patch-bundle --patch-bundle /tmp/officex-patch-bundle.json --candidate-docx /tmp/officex-sandboxes/demo-run/candidate/minimal_writer_demo.docx --anchor-snapshot /tmp/officex-live-anchor-snapshot.json --dry-run --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex provider list
.venv/bin/python -m tools.report_scaffold_v3.cli officex provider build-request --provider openai --role orchestrator --run-id demo-run --sandbox-root /tmp/officex-sandboxes --config-field api_key=demo --config-field model_id=gpt-5.4 --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex trace checkpoint --title "checkpoint title"
.venv/bin/python -m tools.report_scaffold_v3.cli index-trace
```

Legacy root commands such as `build-word` and `validate-word` remain callable as
deterministic compatibility primitives, but they are not the preferred OfficeX
runtime surface.

## Governance Entry Points

- [PROJECT.md](/Users/nihao/Documents/Playground/document-ops-system/PROJECT.md)
- [AGENTS.md](/Users/nihao/Documents/Playground/document-ops-system/AGENTS.md)
- [docs/ACTIVE_RULES_AND_PATHS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md)
- [docs/ARCHITECTURE.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ARCHITECTURE.md)
- [docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md)
- [docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md)
- [docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md)
- [docs/VISUAL_AUDIT_REQUIREMENTS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/VISUAL_AUDIT_REQUIREMENTS.md)
- [docs/REVIEW_ANCHOR_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/REVIEW_ANCHOR_PROTOCOL.md)
- [docs/CONSTRAINT_INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/CONSTRAINT_INDEX.md)
- [harnesses/INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/INDEX.md)
- [docs/PRODUCT_ROADMAP.md](/Users/nihao/Documents/Playground/document-ops-system/docs/PRODUCT_ROADMAP.md)
