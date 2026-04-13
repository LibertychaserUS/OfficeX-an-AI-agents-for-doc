---
doc_id: mvp_scaffold_lessons_register
layer: register
authority: active_reference
status: living
owner: platform_governance
machine_source_of_truth: false
---

# MVP And Scaffold Lessons Register

## Purpose

This register captures recurring platform lessons from the scaffold and MVP
phases so they are not lost in chat history.

## Lessons

### LESSON-001

- issue: root governance stayed tied to GU2 and LoopMart for too long
- impact: active platform identity and archived case identity blurred together
- control: keep active governance and archived case rules in separate roots

### LESSON-002

- issue: product identity drifted away from the technical package name
- impact: naming and architecture discussions became harder to audit
- control: keep product identity, codename, and compatibility package names
  explicitly separated

### LESSON-003

- issue: early workflow logic treated visual correctness as secondary
- impact: page-layout failures escaped structural checks
- control: elevate render and screenshot audit to first-class status

### LESSON-004

- issue: old frozen virtual environments became unreliable
- impact: historical workspaces were hard to execute safely
- control: keep archived workspaces read-only and build fresh active
  environments in the live platform root

### LESSON-005

- issue: human review was not initially modeled with stable anchors
- impact: precise edits were hard to request and automate safely
- control: require explicit review-anchor protocols for future UI and runtime
  work

### LESSON-006

- issue: AI and program responsibilities were not sharply separated early on
- impact: document mutation logic risked becoming opaque
- control: keep AI on content and generation-code duties; keep exact document
  execution in deterministic program logic
