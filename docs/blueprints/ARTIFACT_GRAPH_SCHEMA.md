---
doc_id: artifact_graph_schema
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Artifact Graph Schema

## Purpose

This document defines the minimum object model for the OfficeX `docx` MVP.

It exists so the platform can behave like a document-task runtime rather than a
freeform editor wrapper.

The graph is the contract between:

- imported source materials
- AI-generated candidate content
- deterministic `docx` execution
- review anchors
- patch proposals
- publication and trace

## Design Rule

Do not treat the raw `.docx` package as the only semantic model.

The `.docx` file is:

- a deliverable artifact
- an execution target
- a renderable projection

It is not sufficient on its own to describe:

- task intent
- review targets
- evidence state
- patch scope
- approval state

## Object Layers

The graph is divided into six layers.

### 1. Run Context Layer

Objects:

- `workspace`
- `run`
- `session`
- `approval_mode`

### 2. Source Layer

Objects:

- `source_document`
- `template_document`
- `brief_document`
- `rubric_document`
- `variable_sheet`
- `asset_source`
- `historical_reference`

### 3. Deliverable Layer

Objects:

- `deliverable`
- `document_version`
- `candidate_document`
- `published_document`

### 4. Structural Layer

Objects:

- `section`
- `paragraph`
- `run_span`
- `table`
- `table_row`
- `table_cell`
- `figure`
- `caption`
- `list_block`
- `metadata_block`

### 5. Control Layer

Objects:

- `constraint_set`
- `page_profile`
- `style_profile`
- `truth_policy`
- `override_record`
- `verification_record`

### 6. Change Layer

Objects:

- `review_anchor`
- `issue_record`
- `patch_bundle`
- `patch_operation`
- `audit_result`
- `promotion_record`

## Core Object Definitions

### workspace

Required fields:

- `workspace_id`
- `root_path`
- `active_profile`
- `active_page_profile`
- `status`

### run

Required fields:

- `run_id`
- `workspace_id`
- `goal`
- `scope`
- `allowed_surfaces`
- `blocked_surfaces`
- `approval_mode`
- `status`

### source_document

Required fields:

- `artifact_id`
- `artifact_kind`
- `path`
- `source_role`
- `mutability`
- `origin`

Allowed `source_role` values:

- `template`
- `brief`
- `rubric`
- `reference_sample`
- `legacy_case_reference`
- `source_notes`
- `variable_source`

Allowed `mutability` values:

- `immutable_import`
- `sandbox_copy`
- `archived_reference`

### deliverable

Required fields:

- `deliverable_id`
- `deliverable_type`
- `primary_format`
- `compatibility_target`
- `current_candidate_id`

For the current MVP:

- `deliverable_type = formal_document`
- `primary_format = docx`
- `compatibility_target = microsoft_word`

### section

Required fields:

- `section_id`
- `document_id`
- `heading_level`
- `title`
- `order_index`
- `parent_section_id`

### paragraph

Required fields:

- `paragraph_id`
- `document_id`
- `section_id`
- `style_role`
- `order_index`

### run_span

Required fields:

- `run_span_id`
- `paragraph_id`
- `text`
- `effective_style_ref`

### figure

Required fields:

- `figure_id`
- `document_id`
- `section_id`
- `asset_ref`
- `anchor_ref`
- `caption_id`
- `numbering_ref`

### caption

Required fields:

- `caption_id`
- `owner_kind`
- `owner_id`
- `text`
- `style_role`

### review_anchor

Required fields:

- `anchor_id`
- `document_id`
- `target_kind`
- `target_id`
- `page_hint`
- `selector`

Allowed `target_kind` values:

- `section`
- `paragraph`
- `run_span`
- `table`
- `figure`
- `caption`

### issue_record

Required fields:

- `issue_id`
- `anchor_id`
- `issue_kind`
- `severity`
- `status`
- `evidence_scope`

### patch_bundle

Required fields:

- `patch_bundle_id`
- `run_id`
- `target_document_id`
- `operations`
- `approval_requirements`
- `verification_requirements`

## Identity Rules

- Every mutable object must have a stable id.
- Human-visible page numbers are hints, not primary identity.
- Structural ids must survive re-render whenever possible.
- Sandbox copies must preserve object ids unless a transform explicitly
  invalidates them.

## Mutability Rules

Mutable objects live only in:

- sandbox copies
- generated assets
- active candidates
- patch bundles

Immutable objects include:

- imports
- archived case-study materials
- published historical artifacts

## Truth Rules

The graph distinguishes:

- `source truth`
- `candidate truth`
- `execution truth`
- `approval truth`

No single object should claim all four.

## Minimal MVP Coverage

The first implementation only needs to fully support:

- cover/metadata blocks
- headings
- paragraphs
- run spans
- simple tables
- inline figures
- captions
- review anchors
- patch bundles
- verification records

Complex floating objects, text boxes, and advanced nested drawing structures
may be represented later as extended object kinds.
