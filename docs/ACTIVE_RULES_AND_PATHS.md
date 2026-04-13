# Active Rules And Paths

## Purpose

This document defines the active development boundary for `Document Operations
System`.

Use it as the first answer to:

- which rules are active
- which directories are editable
- which paths are archived
- which names are compatibility-only
- which blueprint and register files are current

## Active Governance

The active platform rules are:

- [AGENTS.md](/Users/nihao/Documents/Playground/document-ops-system/AGENTS.md)
- [PROJECT.md](/Users/nihao/Documents/Playground/document-ops-system/PROJECT.md)
- [docs/CONSTRAINT_INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/CONSTRAINT_INDEX.md)
- [docs/WORKFLOW_OPERATING_MODEL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/WORKFLOW_OPERATING_MODEL.md)
- [docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md)
- [docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md)
- [docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md)
- [docs/blueprints/OFFICEX_AGENT_SYSTEM.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_AGENT_SYSTEM.md)
- [docs/blueprints/DOMAIN_AGENT_REGISTRY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DOMAIN_AGENT_REGISTRY.md)
- [manifests/agent_catalog.yml](/Users/nihao/Documents/Playground/document-ops-system/manifests/agent_catalog.yml)
- [docs/blueprints/PROMPT_EVOLUTION_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROMPT_EVOLUTION_PROTOCOL.md)
- [docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md)
- [docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md)
- [manifests/provider_catalog.yml](/Users/nihao/Documents/Playground/document-ops-system/manifests/provider_catalog.yml)
- [docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md)
- [docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md)
- [docs/blueprints/DEVELOPMENT_RETROSPECTIVE_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DEVELOPMENT_RETROSPECTIVE_PROTOCOL.md)
- [docs/blueprints/ARTIFACT_GRAPH_SCHEMA.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/ARTIFACT_GRAPH_SCHEMA.md)
- [docs/blueprints/PATCH_PROPOSAL_SCHEMA.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PATCH_PROPOSAL_SCHEMA.md)
- [docs/blueprints/AUTOMATION_TASK_PACKET_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/AUTOMATION_TASK_PACKET_CONTRACT.md)
- [docs/REVIEW_ANCHOR_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/REVIEW_ANCHOR_PROTOCOL.md)
- [docs/VISUAL_AUDIT_REQUIREMENTS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/VISUAL_AUDIT_REQUIREMENTS.md)
- [docs/OPEN_SOURCE_EDITOR_EVALUATION.md](/Users/nihao/Documents/Playground/document-ops-system/docs/OPEN_SOURCE_EDITOR_EVALUATION.md)
- [harnesses/INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/INDEX.md)
- [docs/PRODUCT_ROADMAP.md](/Users/nihao/Documents/Playground/document-ops-system/docs/PRODUCT_ROADMAP.md)
- [docs/ENGINEERING_ISSUES_REGISTER.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ENGINEERING_ISSUES_REGISTER.md)
- [docs/development/INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/development/INDEX.md)
- `/Users/nihao/Documents/Playground/document-ops-system/docs/registers`

These files are the source of truth for current platform work.

The active development-workflow layer lives under:

- `/Users/nihao/Documents/Playground/document-ops-system/docs/development`

These files govern how OfficeX is developed and reviewed.

They do not redefine the OfficeX product runtime.

The active platform trace root is:

- `/Users/nihao/Documents/Playground/document-ops-system/trace`

Use local trace files for current work. Do not resume from archived case-study
trace files unless the task is explicitly historical.

## Active Runtime CLI Surface

Current supported OfficeX runtime command families are:

- `officex workspace`
- `officex sandbox`
- `officex task`
- `officex provider`
- `officex prompt`
- `officex agent`
- `officex trace`

Preferred runtime entrypoints currently include:

- `officex workspace init`
- `officex sandbox create`
- `officex task run-docx-mvp`
- `officex task inspect`
- `officex task build-review-ledger`
- `officex task extract-anchors`
- `officex task apply-patch-bundle`
- `officex provider list`
- `officex provider show`
- `officex provider build-request`
- `officex prompt show`
- `officex agent list`
- `officex agent show`
- `officex trace checkpoint`

Legacy root commands such as `build-word`, `validate-word`, and
`run-section-pipeline` remain available only as deterministic compatibility
primitives.

## Active Sandboxes

The active document-editing sandbox root is:

- `/Users/nihao/Documents/Playground/document-ops-system/sandboxes`

All interactive editor sessions, patch previews, and mutable document copies
should be created there instead of editing imported references directly.

## Active Development Root

Edit here by default:

- `/Users/nihao/Documents/Playground/document-ops-system`

Treat this as the only active platform workspace unless the user explicitly
asks for a different target.

## Archived Product Workspace

Read-only by default:

- `/Users/nihao/Documents/Playground/archive/products/loopmart/LoopMart-GU2-rebuild`

Use this only for:

- audit
- historical review
- case-study reference
- recovery of old evidence

Archived case-study docs inside `/Users/nihao/Documents/Playground/document-ops-system/docs/archive`
are also read-only by default.

## Reference Corpus

Agent CLI reference materials are stored separately from both active platform
code and archived products:

- official references:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official`
- secondary references:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/secondary`
- research index:
  - [docs/research/AGENT_CLI_REFERENCE_INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/research/AGENT_CLI_REFERENCE_INDEX.md)

Treat these as reference-only inputs for planning and comparison.

## Historical Root Snapshots

The previous root governance files were snapshotted to:

- `/Users/nihao/Documents/Playground/meta_archive/gu2_governance_2026-04-11`

These are historical records, not active rules.

## Removed Legacy Archive

The deleted legacy archive is recorded at:

- [docs/archive/LOOPMART_LEGACY_ARCHIVE_TOMBSTONE.md](/Users/nihao/Documents/Playground/document-ops-system/docs/archive/LOOPMART_LEGACY_ARCHIVE_TOMBSTONE.md)

Do not recreate or depend on the removed path.

## Compatibility Names

The product name is:

- `Document Operations System`

The active internal codename for the app surface is:

- `OfficeX`

The internal compatibility package remains:

- `tools.report_scaffold_v3`

Use the product name for governance and product docs.
Use the compatibility package name only when referring to current code imports
or CLI module paths.
