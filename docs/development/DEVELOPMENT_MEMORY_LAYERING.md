---
doc_id: development_memory_layering
layer: operational
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Development Memory Layering

## Purpose

This document defines how OfficeX development memory should be organized.

It does not define product runtime memory.

## Layers

### 1. Development Constitution Memory

Contains stable development rules such as:

- project boundary discipline
- runtime-first implementation rules
- product/runtime separation
- approval and review discipline

This layer should change rarely.

### 2. Project Working Memory

Contains active development state such as:

- current stage
- active architecture decisions
- current blockers
- current runtime status
- near-term implementation order

This layer is primarily captured through:

- checkpoints
- current state
- development review registers

### 3. Agent Review Memory

Contains reusable review observations from development critique passes such as:

- repeated coupling issues
- repeated UX overcomplexity
- repeated test blind spots
- recurring runtime mistakes

This layer is advisory and should feed proposals, not directly change active
rules.

## Hard Rule

Development memory may improve implementation flow.

It may not silently override:

- OfficeX constitution
- product runtime contracts
- approved registries

## Storage Rule

Development memory should live in:

- checkpoints
- development registers
- development workflow docs

It should not be smuggled into product runtime manifests.
