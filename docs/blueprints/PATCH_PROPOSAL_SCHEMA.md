---
doc_id: patch_proposal_schema
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Patch Proposal Schema

## Purpose

This document defines the format of a patch proposal in the OfficeX `docx` MVP.

Patch proposals are the bridge between:

- agent output
- deterministic document mutation
- human approval
- verification

## Core Rule

AI does not directly mutate the final document.

AI may produce:

- replacement text
- restructuring intent
- issue classifications
- asset-generation code
- patch suggestions

The runtime must convert those into a bounded patch proposal before execution.

## Patch Bundle Shape

A patch bundle contains:

- metadata
- target document reference
- one or more patch operations
- approval requirements
- verification requirements

## Required Top-Level Fields

- `patch_bundle_id`
- `run_id`
- `target_document_id`
- `generated_by`
- `patch_intent`
- `operations`
- `approval_mode`
- `approval_requirements`
- `verification_requirements`

## patch_intent

Allowed values:

- `content_revision`
- `style_alignment`
- `layout_repair`
- `asset_insertion`
- `metadata_update`
- `mixed`

## Operation Kinds

The MVP supports these operation kinds:

- `replace_text`
- `insert_paragraph`
- `delete_paragraph`
- `restyle_paragraph`
- `restyle_run_span`
- `insert_figure`
- `replace_figure`
- `update_caption`
- `renumber_sequence`
- `update_page_profile`
- `bind_keep_together`

## Required Fields Per Operation

- `operation_id`
- `operation_kind`
- `target_anchor_id`
- `allowed_scope`
- `proposed_change`
- `risk_level`
- `requires_user_confirmation`
- `executor_kind`
- `expected_effects`

## allowed_scope

Examples:

- `single_run_span`
- `single_paragraph`
- `single_section`
- `single_figure_block`
- `metadata_block_only`

## risk_level

Allowed values:

- `low`
- `medium`
- `high`
- `prohibited`

## executor_kind

Allowed values:

- `ooxml_text_executor`
- `ooxml_style_executor`
- `ooxml_layout_executor`
- `asset_pipeline_executor`
- `metadata_executor`

## Approval Model

Patch bundles are executed under one of these modes:

- `review_only`
- `ask_every_conflict`
- `scoped_auto_low_medium`
- `full_auto_in_sandbox`

High-risk operations still require confirmation.
Prohibited operations never execute.

## Verification Model

Allowed verification scopes:

- `structural`
- `style`
- `layout`
- `visual`
- `mixed`

## Non-Negotiable Rules

- No patch may mutate archived references.
- No patch may mutate immutable imports directly.
- No patch may silently expand scope beyond its declared anchor and scope.
- No patch may present unverified content as verified fact.
- No patch may bypass deterministic executors.

## Minimal MVP Strategy

The first implementation should support a small subset well:

- replace text
- insert paragraph
- restyle paragraph
- insert figure
- update caption
- bind keep-together
- update page profile
