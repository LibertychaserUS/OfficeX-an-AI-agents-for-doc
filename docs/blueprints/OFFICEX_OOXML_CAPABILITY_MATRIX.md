---
doc_id: officex_ooxml_capability_matrix
layer: blueprint
authority: active
status: living
owner: platform_engineering
machine_source_of_truth: false
---

# OfficeX OOXML Capability Matrix

## Purpose

OfficeX does not need to recreate every editor feature exposed by Word or
OnlyOffice.

It needs a bounded, high-value OOXML mutation capability set for the target
deliverable workflows.

## Coverage Model

Each capability should be classified as:

- direct library support
- OOXML extension required
- deferred

## Priority Capabilities

### P0: Required For `docx` MVP

- paragraph text replacement
- paragraph insertion
- paragraph style updates
- heading hierarchy handling
- table creation and bounded table updates
- image insertion with sizing controls
- caption creation and numbering
- page profile and section settings used by the active template
- cover/body separation
- appendix-safe section routing

### P1: Needed Soon After MVP

- cross-reference aware citation placement
- code block styling conventions
- keep-together helpers for figure and caption groups
- conservative fallback wrappers such as borderless-table grouping

### Deferred

- broad text-box editing
- floating-shape parity with rich editor behavior
- complex SmartArt-like constructs
- exhaustive editor-specific niche controls

## Engineering Rule

The matrix should be driven by:

- actual OfficeX target workflows
- repeated failure patterns
- benchmark value

It should not be driven by "editor completeness" as an abstract goal.
