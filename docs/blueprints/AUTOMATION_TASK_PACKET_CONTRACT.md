---
doc_id: automation_task_packet_contract
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Automation Task Packet Contract

## Purpose

This document defines the minimum contract for running OfficeX work through
automation without target drift.

## Design Rule

Automation should never be driven by a loose prompt alone.

Every automated run should receive a structured task packet.

## Task Packet Fields

Required fields:

- `task_packet_id`
- `goal`
- `task_family`
- `active_workspace`
- `allowed_surfaces`
- `blocked_surfaces`
- `input_artifacts`
- `constraints`
- `approval_mode`
- `acceptance_gates`
- `publish_gate`

Recommended fields:

- `priority`
- `deadline_hint`
- `reference_corpora`
- `expected_outputs`
- `fallback_behavior`
- `rollback_behavior`

## task_family

Allowed values should align with harnesses:

- `document_ingestion`
- `document_generation`
- `document_revision`
- `template_alignment`
- `asset_binding`
- `compliance_review`
- `render_audit`
- `publication_release`

## approval_mode

Allowed values:

- `review_only`
- `ask_every_conflict`
- `scoped_auto_low_medium`
- `full_auto_in_sandbox`

## acceptance_gates

Examples:

- candidate opens in Word
- page profile matches the selected profile
- no prohibited truthfulness violations
- structural audit passes
- visual audit warnings do not exceed threshold

## publish_gate

Allowed values:

- `never_publish`
- `publish_after_human_review`
- `publish_if_all_gates_pass_and_user_preapproved`

## Why This Matters

Without a task packet, automation becomes prompt-driven improvisation rather
than governed execution.

## Minimal MVP Rule

The first automation implementation does not need to expose every field in the
UI, but the schema itself should already exist.
