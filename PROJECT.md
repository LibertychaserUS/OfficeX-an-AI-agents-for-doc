# PROJECT.md

## Product Charter

`Document Operations System` is the active platform root.

The current internal codename for the product surface is:

- `OfficeX`

The current delivery target is narrower than the long-term vision:

- phase focus: `docx` only
- priority: files must open normally in Microsoft Word
- main surface: desktop-first human-in-the-loop app

Its job in this phase is to turn formal deliverable work into a governed
engineering process with:

- explicit source layers
- controlled transforms
- programmatic document mutation
- auditable review flows
- replayable execution
- benchmark-aware validation

## Current Product Boundary

This project is the active platform root:

- `/Users/nihao/Documents/Playground/document-ops-system`

It is separate from archived product workspaces.

## Current MVP Direction

The current MVP is a `docx-first deliverable runtime`.

Core operating rules for this MVP:

- AI may generate text, plans, review findings, and image/chart generation code.
- AI should not directly mutate Office document structure as a source of truth.
- Programmatic transforms own `docx` structure, styles, layout, numbering, asset
  insertion, and export integrity.
- The active collaboration model is `platform truth + Office mirror`.
- Conflict handling is human-first by default, with scoped user-granted
  autonomy for lower-risk cases.

See:

- [docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md)
- [docs/blueprints/OFFICEX_AGENT_SYSTEM.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_AGENT_SYSTEM.md)
- [docs/blueprints/DOMAIN_AGENT_REGISTRY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DOMAIN_AGENT_REGISTRY.md)
- [docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md)
- [docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md)
- [docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md)
- [docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md)
- [docs/PRODUCT_ROADMAP.md](/Users/nihao/Documents/Playground/document-ops-system/docs/PRODUCT_ROADMAP.md)
- [docs/ACTIVE_RULES_AND_PATHS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md)

## Non-Goals For This Phase

This phase does not attempt to:

- rename the internal Python package away from `tools.report_scaffold_v3`
- support `pptx`, `xlsx`, `pdf`, or Gantt as first-class outputs
- make the embedded editor the sole truth source
- rewrite the core transformation engine from scratch
- keep legacy case-study rules as root product governance

## Quality Gates

Work is not complete until:

1. the chosen harness or workflow path is clear
2. edits are localized to the intended truth layer
3. validation scope is stated honestly
4. `docx` outputs open normally in Microsoft Word
5. A4/page-layout constraints are explicit rather than implied
6. visual/layout risks are checked at the correct scope
7. tests or smoke checks pass, or the blocker is recorded explicitly
8. product docs and governance docs match the implementation state

## Product Layers

The platform is organized as:

1. product governance
2. contracts and manifests
3. execution harnesses
4. deterministic transformation and audit code
5. outputs, release notes, and trace
6. roadmap, archive, and case-study records

## Archive Relationship

Archived product workspaces live under:

- `/Users/nihao/Documents/LegacyArchives/gu2-loopmart-outside-playground`

They remain available for future review and audit, but they are not the active
platform project.
