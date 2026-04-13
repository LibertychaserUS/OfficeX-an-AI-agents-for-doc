# Write Contract

## Purpose

The write contract is the mainline rule layer that tells the platform how to
write candidate Word content from explicit roles. It is not the deferred
strict-template branch and it is not a sample-fitting mechanism.

## Current Scope

The first version is intentionally narrow:

- write paragraph blocks from declared roles,
- write image blocks with declared image rules,
- start from the official English template as the base document,
- clear inherited body content before writing new candidate content,
- emit candidate outputs only inside `outputs/builds/`.

## Contract Files

- `manifests/write_contract.yml`
- `sources/minimal_build.yml`

## Rule Model

`paragraph_roles` define:

- target Word style,
- paragraph-level format that must be written explicitly,
- run-level format that must be written explicitly,
- whether mixed-run content is allowed.

`image_roles` define:

- which caption role to use,
- how image width is resolved,
- whether the image paragraph is centered.

## Guardrails

- Imported reference documents remain untouched.
- The English template remains the formatting authority.
- Writer output is a candidate artifact, not an in-place modification.
- The writer must reject undefined roles instead of guessing.
