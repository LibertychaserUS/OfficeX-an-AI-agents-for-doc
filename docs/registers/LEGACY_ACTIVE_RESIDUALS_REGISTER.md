---
doc_id: legacy_active_residuals_register
layer: register
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Legacy Active Residuals Register

## Purpose

This register tracks remaining active-path legacy bindings that still reflect
the old GU2 or report-scaffold line and may need future migration.

## Active Residuals

### RESIDUAL-001

- area: internal package compatibility name
- current state: active code and CLI still use `tools.report_scaffold_v3`
- risk: naming drift and conceptual confusion
- status: accepted for current phase

### RESIDUAL-002

- area: default baseline and template manifests
- current state: `baseline.yml` and `template_profile.yml` still point to legacy
  imported sample files from the GU2 line
- risk: accidental reuse of legacy sample defaults during new product work
- status: open

### RESIDUAL-003

- area: sample template contracts
- current state: template contracts still describe the legacy imported sample
  pair
- risk: developers may mistake sample defaults for universal product defaults
- status: mitigated by explicit legacy wording, not yet fully replaced

### RESIDUAL-004

- area: archived-case bootstrap stage
- current state: resume bootstrap still includes archived LoopMart context as a
  later stage
- risk: unnecessary historical loading if future runs ignore stage boundaries
- status: accepted with caution
