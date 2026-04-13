---
doc_id: officex_editor_compatibility_and_callability
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Editor Compatibility And Callability

## Decision

For the current `docx` MVP:

- preferred embedded editor surface: `ONLYOFFICE Docs Community Edition`
- comparison and fallback reference: `Collabora Online`
- final acceptance renderer: `Microsoft Word`

## Why This Split Exists

The embedded editor and Microsoft Word solve different problems.

The embedded editor gives:

- a familiar Office-style surface
- a controllable collaboration canvas
- local app embedding potential

Microsoft Word gives:

- the final compatibility target for the generated `docx`
- the final acceptance renderer for openability and practical submission use

## ONLYOFFICE Callability

The current MVP should assume this integration shape:

- host the editor as a web surface inside the desktop shell
- instantiate and destroy editor sessions explicitly
- treat editor events and file lifecycle as the main integration contract
- keep deterministic document mutation in the Python runtime

This choice is grounded in the official Docs API object model, where the editor
is created as a managed object and supports lifecycle operations such as editor
reinitialization.

## ONLYOFFICE Boundary

Do not assume advanced editor-external mutation hooks as the MVP baseline.

The MVP should remain viable if the practical integration surface is limited to:

- open document
- save document
- reload document
- detect document dirty state
- show a familiar editing/review surface

This keeps the app compatible with an open-source-first deployment model.

## Collabora Comparison Value

`Collabora Online` remains important because it exposes a strong open-source
integration story with:

- WOPI-centered hosting and file contracts
- postMessage API for host/editor interaction
- proven browser-based office surface patterns

It is valuable as a long-term comparison point, but it is not the first
embedded target for this MVP.

## Compatibility Rule

OfficeX should treat compatibility in three layers:

1. structural compatibility
   - valid OOXML package
   - correct relationships, media, numbering, and styles
2. editor-surface compatibility
   - sandbox copy opens inside the embedded editor
   - expected save/reload loop works
3. Microsoft Word acceptance compatibility
   - file opens normally in Word
   - page profile is correct
   - major visual/layout issues are absent or auditable

## Practical Constraint

No embedded open-source editor should be treated as a proof that Microsoft Word
will render identically.

The app therefore needs:

- explicit page profiles
- visual audit
- cross-renderer checks when precision risk is high
- Word-oriented acceptance checks for release candidates

## MVP Integration Rule

The editor layer is callable.
The runtime layer is authoritative.

If there is a disagreement between editor convenience and deterministic runtime
control, prefer the deterministic runtime.
