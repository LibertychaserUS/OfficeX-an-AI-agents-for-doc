# Architecture

## Intent

`Document Operations System` is a multi-agent deliverable runtime.

The current internal codename for the app surface is `OfficeX`.

The current implementation phase is `docx-first`.

It is built to separate:

- governance
- contracts
- execution harnesses
- deterministic transformation engines
- audits
- release and trace

## Layer Order

The preferred layer order is:

1. product governance
2. manifests and managed sources
3. ingestion and transformation engines
4. bounded writers and patchers
5. modular audits and benchmarks
6. sanctioned orchestration
7. release and replay
8. roadmap and external historical references

## Design Principles

- Product identity is broader than any one report or case study.
- Precision should come from explicit manifests and repeatable transforms.
- `docx` mutation should be programmatic and auditable.
- AI should generate content or generation code, not silently mutate document
  structure as the final authority.
- High-impact changes should remain reviewable by humans.
- Validation scope must be stated honestly.
- Archived product workspaces may inform the platform without governing it.

## Current Architectural Frame

The current MVP frame is:

- active output type: `docx`
- target compatibility: Microsoft Word
- truth model: `platform truth + Office mirror`
- collaboration mode: human-first with scoped adaptive autonomy
- top product entry: `officex`
- first app shell shape: intake-first macOS desktop workbench
- page profile: explicit, with `A4` treated as a managed constraint when
  required by the deliverable

## Core Runtime Layers

### Product Entry Layer

- `officex` console entry
- desktop-app launcher
- intake-first desktop workbench
- machine-local settings boundary
- bounded action routing for `doctor`, `render-boundary`, and controlled task runs

### Surface Layer

- desktop-first app shell
- left workspace and thread rail
- center intake and document surface
- right chat, confirmation, and utility dock
- initial thread state: blank chat intake followed by task confirmation card
- utility actions and candidate/report viewing inside the workbench flow
- first-launch setup remains machine-local and secondary to task intake
- later hybrid review canvas
- later Office-like document mirror for familiar human editing and review

### Runtime Layer

- orchestrator
- constraint analyst
- writer instances
- asset engineer
- patch and assembly engineer
- validation and review auditor

Detailed agent typing and runtime fan-out rules live in:

- [docs/blueprints/OFFICEX_AGENT_SYSTEM.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_AGENT_SYSTEM.md)

### Deterministic Execution Layer

- OOXML-native `docx` reader/writer
- style and layout application
- asset insertion and numbering
- patch execution
- export integrity checks

### Audit Layer

- structural audit
- compliance audit
- render audit
- visual anomaly checks
- environment-readiness audit
- renderer-boundary benchmark

### State Layer

- manifests
- constraints
- trace and checkpoints
- issue registers
- bounded memory and replay indexes
- versioned prompt packs
- domain-agent registry
- provider adapters

## Execution Modes

### Product Readiness

Use this when the main goal is to determine whether the current Mac, provider
environment, and renderer setup are ready for OfficeX.

The current concrete actions are:

- `officex doctor`
- `officex render-boundary`

### Structured Generation

Use this when content is managed through manifests, sections, figures,
citations, and snippets.

### Controlled Revision

Use this when a copied target document needs a bounded, auditable patch.

### Audit And Compliance

Use this when the main goal is checking structure, layout, evidence binding, or
conformance rather than changing content.

### Release And Replay

Use this when canonical outputs, summaries, or checkpoint indexes need to be
updated in a controlled way.

## Archive Relationship

Archived product workspaces live under:

- `/Users/nihao/Documents/LegacyArchives/gu2-loopmart-outside-playground`
