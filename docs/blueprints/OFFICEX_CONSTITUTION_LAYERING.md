---
doc_id: officex_constitution_layering
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Constitution Layering

## Purpose

This document prevents the OfficeX constitution from becoming a loose idea
document.

The constitution must stay:

- low-level
- stable
- enforceable
- difficult to override accidentally

## Layering Rule

The constitutional stack must be split into five layers.

### Layer 0: Core Invariants

These are hard system rules.

Examples:

- deterministic mutation is the only write authority
- imported sources and archived references are immutable
- high-risk changes require explicit human approval
- evidence-backed claims outrank fluent unsupported prose
- replayable artifacts outrank implicit runtime state

### Layer 1: Document Quality Layers

These define what must be checked and repaired.

OfficeX currently uses:

- semantic layer
- structural layer
- layout layer
- rendering layer
- review layer

### Layer 2: Operation Rules

These define what runtime operations are allowed.

Examples:

- replace paragraph text
- insert paragraph after anchor
- update paragraph style
- bind caption to figure
- enforce page profile

This layer should be typed and executable.

### Layer 3: Approval And Risk Rules

These define when the runtime may:

- auto-execute
- propose only
- ask the user
- refuse outright

This layer must remain explicit and versioned.

### Layer 4: Domain And User Extension Rules

These are configurable but may not break higher layers.

Examples:

- company template profile
- academic citation profile
- legal wording review pack
- user writing preferences
- project-specific materials catalog

## Hard Separation Rule

The following may extend OfficeX but may not override core invariants directly:

- prompt packs
- domain packs
- user memory
- project memory
- provider configuration

## Encoding Strategy

The constitution should be expressed through:

- schemas
- enums
- registries
- policy manifests
- deterministic validators

It should not rely on free-form prompt text alone.

## Practical Outcome

When new requirements appear, OfficeX should not patch the constitution first.

It should first determine whether the requirement belongs to:

- a quality layer
- an operation rule
- an approval rule
- a domain extension
- a user preference

Only true cross-cutting invariants should modify the constitution.
