---
doc_id: development_retrospective_protocol
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Development Retrospective Protocol

## Purpose

This document defines how OfficeX should reflect on its own engineering history
at the end of each major development stage.

This protocol is about platform development history.

It is not the same thing as per-run runtime audit output.

## Core Rule

Every major implementation stage should end with a concise retrospective that
records:

- what the stage tried to achieve
- what actually changed
- what worked
- what failed
- what remained coupled or fragile
- what assumptions were wrong
- what must carry forward into the next stage

## Required Stage Boundaries

Retrospectives are required for stages such as:

- foundation and governance setup
- CLI/runtime restructuring
- sandbox lifecycle implementation
- prompt/runtime composition changes
- provider adapter integration
- desktop shell integration
- editor mirror integration
- validation or audit expansion
- release baseline creation

## Minimum Retrospective Fields

Each retrospective should include:

- `stage_id`
- `time_range`
- `goal`
- `implemented_changes`
- `verification_completed`
- `design_mistakes_or_misreads`
- `active_risks`
- `carry_forward_rules`
- `next_stage_focus`

## Storage Rule

The primary durable home for stage retrospectives is the local trace and
checkpoint chain.

Optional summary/index material may also live in a register.

## Review Rule

Retrospectives should be factual, not ceremonial.

They should explicitly call out:

- unnecessary complexity
- legacy leakage
- incorrect assumptions
- weak tests
- architecture mismatch

## Relationship To Runtime Stage Reviews

Runtime stage reviews are operational artifacts for one task run.

Development retrospectives are engineering-history artifacts for OfficeX itself.

Do not confuse them.
