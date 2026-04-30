---
doc_id: officex_document_edit_sandbox
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Document Edit Sandbox

## Purpose

This document defines how mutable document work should be isolated during the
`docx` MVP.

The sandbox exists to prevent:

- accidental mutation of imported references
- accidental mutation of archived case-study files
- editor-surface writes bypassing platform trace and patch review
- cross-run contamination between unrelated editing sessions

## Sandbox Root

The active sandbox root is:

- `/Users/nihao/Documents/Playground/document-ops-system/sandboxes`

Each run should create a dedicated subdirectory under that root.

## Sandbox Contents

Each sandbox should contain:

- copied mutable `docx` working file
- immutable import manifest snapshot
- generated assets for that run
- patch proposal artifacts
- audit outputs
- save/export logs
- promotion metadata

## Truth Boundary

Imported references remain immutable:

- `/Users/nihao/Documents/Playground/document-ops-system/imports`

Archived cases remain immutable:

- `/Users/nihao/Documents/LegacyArchives/gu2-loopmart-outside-playground`

The editor surface may open only sandbox copies for active editing.

## Required Workflow

1. import source files and contracts
2. create sandbox
3. copy mutable working files into sandbox
4. point the embedded editor at the sandbox copy
5. apply deterministic mutations only to the sandbox copy
6. audit the sandbox output
7. promote approved sandbox result into candidate/output state

## Promotion Rule

Do not promote a sandbox document unless:

- requested changes were bounded and applied to the correct file
- structural checks passed
- relevant visual/layout checks passed
- approval state is satisfied
- trace can explain what was promoted and why

## Editor Rule

The embedded editor is a mirror and collaboration surface, not the final
authority.

The runtime remains responsible for:

- patch execution
- layout repair
- asset insertion
- final candidate export
- trace and replay

## Failure Handling

If a sandbox session becomes inconsistent:

- discard the sandbox copy
- preserve the logs and audit output if useful
- recreate the sandbox from immutable inputs

Never repair a broken sandbox by mutating the archived source or original
import in place.
