---
doc_id: officex_docx_mvp_blueprint
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX `docx` MVP Blueprint

## Current Frame

`OfficeX` is the current internal codename for the app surface built on top of
`Document Operations System`.

This MVP is intentionally narrow:

- output type: `docx`
- compatibility target: Microsoft Word
- primary surface: desktop-first
- interaction model: hybrid review canvas

## Hard Principles

1. AI writes text, review findings, and asset-generation code.
2. Program logic owns `docx` structure, style, numbering, layout, and export.
3. The collaboration model is `platform truth + Office mirror`.
4. Human approval is the default conflict policy.
5. User-granted scoped autonomy may resolve lower-risk conflicts in one run.
6. Visual audit is mandatory for layout-sensitive risks.

## Recommended MVP Surface

Use `ONLYOFFICE Docs Community Edition` as the preferred open-source embedded
editor candidate for the MVP document surface.

Rationale:

- strong `docx`/OOXML orientation
- browser-embeddable document editor
- fits a desktop app plus web companion architecture
- closer to the Microsoft Word user expectation for this phase

Keep `Collabora Online` as a benchmark and fallback reference, especially for
open-source integration patterns and long-term comparison.

The embedded editor is a collaboration surface, not the sole truth source.
It should operate on sandbox copies and controlled save/promote flows.

## Runtime Shape

### Surface

- desktop shell
- Office-like document canvas
- structure tree
- issue and patch panel
- plan and agent panel
- sandbox/session status panel

### Agents

- orchestrator
- section-writing agents
- asset agents for charts, tables, diagrams, and generated images
- evidence and truth review packs
- review agents for quality, professionalism, feasibility, and domain wording
- integrator

### Deterministic Engine

- OOXML-native `docx` read/write
- style application
- page-profile enforcement
- asset insertion
- numbering and caption binding
- patch execution

### Audit Lane

- structural audit
- compliance audit
- render audit
- screenshot-based visual audit when needed

## Canonical Workflow

1. Import prompt, template, brief, rubric, variables, and raw sources.
2. Parse constraints and detect missing high-risk inputs.
3. Build a run plan and classify approval mode.
4. Create a document-edit sandbox and copy imported references into bounded
   mutable workspace files.
5. Generate section text and asset-generation code through AI.
6. Convert AI output into structured program inputs and patch proposals.
7. Execute `docx` writes and layout changes through deterministic code inside
   the sandbox.
8. Run structural plus visual audits.
9. Present reviewable patches and sandbox diffs in the canvas.
10. Apply approved changes and export a Word-compatible candidate.
11. Record trace and publish only verified state.

## MVP Acceptance Criteria

- generated `docx` opens normally in Microsoft Word
- page profile is explicit and correct
- font and style application is deterministic
- figure and caption remain logically and visually bound
- abnormal whitespace and pagination anomalies are auditable
- human can point to exact review locations and request bounded changes

## Deferred Beyond MVP

- `pptx`, `xlsx`, `pdf`, and Gantt as first-class outputs
- direct Microsoft Office add-ins
- autonomous no-review publish flows
- domain-specific legal or financial authority engines
