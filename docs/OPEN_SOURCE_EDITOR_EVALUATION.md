---
doc_id: open_source_editor_evaluation
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Open-Source Editor Evaluation

## Decision Summary

For the current `docx` MVP, prefer:

- `ONLYOFFICE Docs Community Edition`

Keep as active comparison and fallback:

- `Collabora Online`

## Why `ONLYOFFICE` First

- `docx` is the current first-class format
- Microsoft Word compatibility is the current acceptance target
- the editor surface is closer to the user expectation for Office-style review
- it is suitable as an embedded collaboration mirror in a desktop-first app
- official Docs API provides an explicit editor object lifecycle, including
  reinitialization and save-state hooks

## Why `Collabora` Stays Important

- strong open-source integration story
- strong comparison point for long-term editor strategy
- useful reference for self-hosting and integration patterns
- official SDK and WOPI/postMessage model are valuable for future deep
  integration design

## Non-Negotiable Boundary

The embedded editor is not the sole truth source.

Programmatic runtime state and auditable patches remain the authority for:

- generated changes
- layout repair operations
- asset insertion
- trace and replay

## Evaluation Criteria

The chosen editor layer must support:

- open-source availability
- self-hosting
- embeddable web surface
- stable `docx` editing or preview
- acceptable Office-like review experience
- future hook points for comments, patch previews, and anchored review
- acceptable local callability from a desktop shell
- clear boundary between editor-surface interactions and deterministic runtime
  writes

## Current Callability Caveat

`ONLYOFFICE Docs Community Edition` is the current preferred editor surface, but
the MVP should assume a conservative integration shape:

- embed the editor as a document mirror and familiar editing surface
- rely on file open/save lifecycle, editor events, and controlled reloads
- do not assume developer-only connector APIs as a baseline capability

This keeps the MVP inside fully open-source and broadly reproducible boundaries.

## Active Risk Note

Before wider distribution or commercial packaging decisions, perform a dedicated
license and redistribution review for the chosen editor stack.
