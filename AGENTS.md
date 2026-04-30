# AGENTS.md

This file defines the local working rules for the `Document Operations System`
project.

It governs the platform root at:

- `/Users/nihao/Documents/Playground/document-ops-system`

## Product Identity

This project is a multi-agent document engineering platform.

It is designed to support:

- document ingestion
- structured generation
- controlled revision
- template alignment
- compliance review
- render audit
- publication and replayable trace

It is not limited to one report, one course, or one product case.

## Roles

The platform works through these standing roles:

- `Product Architect`
- `Orchestrator`
- `Platform Engineer`
- `Document Intelligence Engineer`
- `Transformation Engineer`
- `Validation & Benchmark Engineer`
- `Governance & Trace Steward`
- `Reviewer`

One person or agent may cover multiple roles, but the responsibilities remain
distinct.

## Core Working Model

The platform must behave like an engineered system, not an ad hoc document
editing assistant.

Before meaningful changes:

1. identify the active profile or task family
2. classify whether the work is:
   - ingestion
   - generation
   - revision
   - audit
   - release
3. choose the nearest sanctioned harness
4. state the expected verification scope:
   - structural
   - semantic
   - layout
   - mixed
5. verify locally before claiming completion

## Product Rules

- Use profile-driven execution rather than case-specific improvisation.
- Use sanctioned pipelines for dependent stages.
- Keep provenance, replayability, and audit trails first-class.
- Prefer explicit manifests and contracts over hidden document heuristics.
- Keep human review gates available for any high-impact transformation.
- Treat benchmark-aware validation as a product requirement, not a nice-to-have.
- Make authority claims precisely; never present structural checks as semantic proof.

## Authority Model

One orchestrator owns:

- final edits to shared truth layers
- final interpretation of validation
- publication and release claims
- trace and archive notes
- final merge decisions across agent outputs

Sub-agents may explore or implement bounded work, but they do not declare
authoritative project state on their own.

## Protected Boundaries

The platform owns only files inside:

- `/Users/nihao/Documents/Playground/document-ops-system`

Archived product workspaces are read-only by default, including:

- `/Users/nihao/Documents/LegacyArchives/gu2-loopmart-outside-playground`

## Compatibility Rule

The product name is `Document Operations System`.

The internal Python package name remains `tools.report_scaffold_v3` during this
transition period. Treat that as a compatibility detail, not the product name.

## Documentation And Harness Rule

When changing platform direction:

- update `PROJECT.md` for product identity or scope
- update `docs/ARCHITECTURE.md` for layer or subsystem boundaries
- update `docs/CONSTRAINT_INDEX.md` for governance routing
- update `docs/WORKFLOW_OPERATING_MODEL.md` for execution shape
- update `harnesses/` and `manifests/harness_catalog.yml` for recurring task patterns
- update `docs/PRODUCT_ROADMAP.md` for new branches, incubations, or archived cases

## Validation Rule

Every meaningful platform change should be followed by:

1. targeted tests when practical
2. a local command or smoke replay when the change affects operator behavior
3. documentation consistency checks
4. fallout review when paths, ownership, release semantics, or authority claims changed

## Archive Rule

Finished product workspaces and case studies may be archived without becoming
the active governance source.

Historical evidence should be preserved by archive notes and case-study records,
not by leaving old product constraints in charge of the platform.
