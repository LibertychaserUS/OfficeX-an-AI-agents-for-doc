---
doc_id: officex_runtime_constitution
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Runtime Constitution

## Purpose

This document defines the minimum constitutional rules for the `docx` MVP so
future complex features extend from the same core protocol instead of adding
uncontrolled special cases.

## Constitutional Principles

1. Constraints before generation.
2. Programmatic execution before free-form document mutation.
3. Visual audit before layout claims.
4. Human approval before high-impact promotion.
5. Exact scope before patch application.
6. Low coupling between subsystems.

## Object Model Requirement

All precise editing should converge on explicit objects such as:

- section
- paragraph
- run
- figure
- caption
- table
- page anchor
- variable
- evidence item
- review issue
- patch proposal

## AI Boundary

AI may generate:

- text content
- review findings
- chart or image generation code
- patch proposals
- rule translation drafts

AI may not silently become the final authority for:

- OOXML structure
- page setup
- numbering state
- final asset insertion
- final style compliance
- release claims

## Deterministic Execution Rule

The runtime must own:

- `docx` object mutation
- style application
- page profile enforcement
- figure-caption adjacency rules
- numbering and caption identity
- export and validation hooks

## Rule Translation Rule

Imported rubric files or review results may be translated into executable audit
rules, but the translation pipeline must produce:

- explicit rule objects
- clear scope
- auditable provenance
- human-reviewable output

No imported rubric should become executable enforcement through opaque prompt
magic alone.

## Decoupling Rule

Provider adapters, UI, runtime execution, memory, audit, and release layers
must be independently replaceable wherever practical.

Complex features should extend the protocol, not bypass it.
