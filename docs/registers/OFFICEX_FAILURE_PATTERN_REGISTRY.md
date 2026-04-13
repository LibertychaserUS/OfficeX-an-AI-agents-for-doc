---
doc_id: officex_failure_pattern_registry
layer: register
authority: active
status: living
owner: validation_benchmark_engineering
machine_source_of_truth: false
---

# OfficeX Failure Pattern Registry

## Purpose

This register tracks recurring document failure patterns that should eventually
be captured by:

- hard rules
- validators
- conservative fallbacks
- benchmark cases

## Active Patterns

### Figure And Caption Split Across Pages

- primary layer: layout
- secondary layer: rendering
- preferred mitigation: keep-together grouping or conservative container

### Cover Page And Body Spillover

- primary layer: structural
- secondary layer: layout
- preferred mitigation: explicit cover/body separation and conservative blank-space tolerance

### Abnormal Character Or Word Spacing

- primary layer: layout
- secondary layer: rendering
- preferred mitigation: spacing audit plus visual review

### Source, Claim, And Citation Drift

- primary layer: semantic
- secondary layer: review
- preferred mitigation: materials graph validation before final citation emission

### Wrong Code Excerpt In Wrong Section

- primary layer: semantic
- secondary layer: structural
- preferred mitigation: usage-context binding plus section-aware validation

### Diagram Legible At Canvas Level But Not At Content Level

- primary layer: rendering
- secondary layer: layout
- preferred mitigation: internal content-density checks and split/export strategies

### Large-Document Cascading Layout Drift

- primary layer: layout
- secondary layer: rendering
- preferred mitigation: long-document stress benchmarks and conservative fallback rules

## Update Rule

New entries should describe:

- what failed
- which quality layer owns it
- how it should be mitigated
- whether it belongs in hard rules, benchmarks, or manual review
