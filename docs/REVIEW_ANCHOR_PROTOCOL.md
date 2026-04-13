---
doc_id: review_anchor_protocol
layer: policy
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Review Anchor Protocol

## Purpose

This protocol defines how humans and agents point to exact locations in a
`docx` deliverable without relying on vague prose such as "somewhere on page 5".

## Required Anchor Types

Every reviewable candidate should expose stable anchors where possible:

- `section_id`
- `heading_id`
- `paragraph_id`
- `run_id`
- `figure_id`
- `table_id`
- `caption_id`
- `page_anchor`
- `bbox`

`page_anchor` and `bbox` are visual aids. Structural IDs remain the primary
anchor whenever they exist.

## Review Operations

The system should support these bounded user actions:

- comment
- request rewrite
- request move
- request style correction
- request layout correction
- accept patch
- reject patch
- apply local override

## Patch Scope Rule

Every patch proposal must declare:

- target anchor
- intended change type
- allowed mutation scope
- affected constraints
- whether human approval is required

No patch should silently expand beyond its declared scope.

## Conflict Rule

Default behavior:

- ask on each conflict

Scoped autonomy is allowed only when the user explicitly grants freedom for the
current run, task, or workspace.

High-risk conflicts still require ask or refusal.

## Visual Review Rule

When structure alone cannot explain the issue, the system should attach visual
context such as:

- page screenshot
- local crop
- highlighted anchor box
- before/after preview

This is required for:

- abnormal spacing
- figure-caption split
- orphaned heading
- paper-size drift
- image overflow
