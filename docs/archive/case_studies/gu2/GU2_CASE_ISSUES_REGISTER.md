---
doc_id: gu2_case_issues_register
layer: register
authority: active_reference
status: living
owner: platform_governance
machine_source_of_truth: false
---

# GU2 Case Issues Register

## Purpose

This register preserves the key failures and blockers observed during the GU2
report work so they can be turned into durable platform controls.

## Issues

### GU2-001

- problem: newer aligned candidate could render worse than the manually audited
  stable copy in Word
- cause: template alignment and renderer behavior were not fully equivalent
  across environments
- lesson: structural success does not prove cross-renderer stability

### GU2-002

- problem: caption-image split and blank-page risks were not fully closed by
  early checks
- cause: render audit was weaker than structural audit
- lesson: visual audit must be a first-class workflow lane

### GU2-003

- problem: residual font-size warnings remained after revision and alignment
- cause: content-level revision completion and style normalization were treated
  as partially separate concerns
- lesson: style normalization needs its own bounded pass and acceptance rule

### GU2-004

- problem: active candidate and manually audited stable copy diverged in
  practical submission value
- cause: "latest" and "most stable" were not the same thing
- lesson: publication logic must distinguish freshness from trustworthiness

### GU2-005

- problem: render-sensitive issues required manual Word inspection
- cause: the system lacked a strong screenshot-based audit step
- lesson: screenshot and render checks must be formalized, not ad hoc
