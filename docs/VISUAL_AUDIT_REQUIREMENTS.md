---
doc_id: visual_audit_requirements
layer: policy
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Visual Audit Requirements

## Purpose

Some `docx` failures are not reliably detectable through structure-only
inspection. This document defines when visual or render-aware audit is required.

## Required Audit Classes

### Page Geometry

- required page size such as `A4`
- margin drift
- unexpected section break effects
- blank page risk

### Semantic Layout

- figure and caption on the same page when required
- heading not isolated at page end
- table title adjacent to the table
- image not overflowing page width or height

### Typography And Whitespace

- abnormal spaces
- invisible-character artifacts
- font fallback drift
- indentation or line-break anomalies that change the perceived content

### Renderer Drift

- structural intent differs from visual output
- Microsoft Word view differs materially from intermediate render or mirror

## Audit Evidence Sources

Use one or more of:

- OOXML/object inspection
- deterministic layout checks
- rendered page screenshots
- targeted screenshot crops
- OCR-assisted verification when helpful
- human visual review

Screenshot-based checks are first-class, not fallback-only.

## Minimum Pass Criteria

A candidate should not be treated as visually clean unless:

- page profile is correct
- no unresolved same-page binding issue remains for critical figures or tables
- no high-severity whitespace anomaly remains
- no unresolved renderer-drift issue is known

## Escalation Rule

If a structural check passes but a screenshot suggests visible drift, the
visual finding wins until resolved or explicitly waived.
