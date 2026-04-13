---
doc_id: officex_layered_quality_model
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Layered Quality Model

## Purpose

OfficeX must not treat all document defects as one undifferentiated bug class.

Quality judgement is split into five layers.

## 1. Semantic Layer

This layer checks meaning, evidence, and correctness.

Examples:

- factual claim is unsupported
- citation does not support the claim
- code excerpt does not match its title or surrounding explanation
- backend code appears in a frontend-design section
- legal or professional wording is inaccurate or unsafe

## 2. Structural Layer

This layer checks object placement and document organization.

Examples:

- heading hierarchy is broken
- appendix content appears in the body
- figure, table, code block, or citation appears in the wrong section
- cover page content leaks into the main body

## 3. Layout Layer

This layer checks page-profile-aware composition.

Examples:

- figure and caption split across pages
- heading becomes orphaned at page end
- body text intrudes into the cover page area
- abnormal whitespace or spacing appears
- required page size and margins are not respected

## 4. Rendering Layer

This layer checks cross-renderer legibility and output stability.

Examples:

- Word and OnlyOffice differ materially in the visible result
- image is blurry or scaled beyond readable limits
- diagram fits the page but internal labels become unreadable
- page-profile drift materially changes presentation

## 5. Review Layer

This layer checks whether the right level of scrutiny was applied.

Examples:

- high-risk finding was not escalated
- required review pack was not run
- unresolved finding was silently ignored
- approval decision is missing for a risky patch

## Quality Routing Rule

Every OfficeX failure pattern should be mapped to one primary layer and may
carry one secondary layer.

This prevents semantic problems from being "fixed" as if they were only layout
problems, and vice versa.

## Execution Rule

Each layer should prefer the lowest-cost correct remedy:

- semantic layer: evidence or content repair
- structural layer: object relocation or schema repair
- layout layer: bounded page/layout adjustment
- rendering layer: renderer-aware fallback or visual review
- review layer: escalation or gate enforcement
