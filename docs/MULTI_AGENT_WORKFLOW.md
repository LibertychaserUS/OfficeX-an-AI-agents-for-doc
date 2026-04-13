# Multi-Agent Workflow

## Scope

This workflow applies only inside:

- `/Users/nihao/Documents/Playground/document-ops-system`

The detailed OfficeX role system is defined in:

- [docs/blueprints/OFFICEX_AGENT_SYSTEM.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_AGENT_SYSTEM.md)

## Orchestrator Rule

One orchestrator owns:

- task decomposition
- shared assumptions
- final edits to shared truth layers
- final validation interpretation
- trace and release notes

Sub-agents may explore or implement bounded work, but they do not define final
platform state on their own.

## Platform Role Split

- `Product Architect`
  - governance, architecture, roadmap, boundary decisions
- `Document Intelligence Engineer`
  - template reading, structure extraction, ingestion quality
- `Transformation Engineer`
  - build pipelines, patch flows, writer behavior
- `Validation & Benchmark Engineer`
  - audits, severity, benchmark rules, false-positive control
- `Governance & Trace Steward`
  - release notes, replay, archive notes, consistency reviews

## Runtime Agent Split

For the `docx` MVP runtime, use the OfficeX six-role system:

- orchestrator
- constraint analyst
- writer
- asset engineer
- patch and assembly engineer
- validation and review auditor

## Sequencing

1. orchestrator picks task family and harness
2. local critical-path work stays with the orchestrator
3. side investigations may run in parallel
4. final edits and verification return to the orchestrator
5. trace and release updates happen last

## No-Bleed Rules

- Archived product workspaces are read-only by default.
- Sub-agents must not infer platform identity from archived case-study history.
- Local platform docs outrank historical case-study materials.
