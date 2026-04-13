---
doc_id: cross_model_development_review
layer: operational
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Cross-Model Development Review

## Purpose

OfficeX development may use multiple models or critique passes, but this should
be structured.

## Recommended Roles

### Main Implementation Thread

Owns:

- primary coding work
- integration decisions
- final local verification

### Architecture Critique Pass

Owns:

- coupling review
- boundary review
- overengineering detection

### Product And UX Critique Pass

Owns:

- task-first flow review
- user-surface compression
- collaboration friction detection

### Verification Pass

Owns:

- regression checks
- assumptions challenge
- missing-test detection

## Rule

Critique passes may influence implementation decisions.

They do not become authority until reviewed and accepted by the main
implementation thread.

## Intended Outcome

This pattern should improve:

- review quality
- architectural clarity
- implementation discipline

without turning the development workflow into uncontrolled multi-agent churn.
