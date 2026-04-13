---
doc_id: desktop_runtime_contract
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Desktop Runtime Contract

## Purpose

This document defines the current desktop runtime boundary for OfficeX.

## Current MVP Stack

Preferred MVP stack:

- desktop shell: `Electron`
- frontend: `TypeScript` plus web UI stack
- runtime sidecar: `Python`
- embedded document mirror: open-source Office surface, currently favoring
  `ONLYOFFICE Docs Community Edition`

## Platform Priority

The first desktop target should be:

- macOS first

The desktop runtime should still preserve future portability to other systems.

## Architectural Split

### Renderer Layer

Owns:

- app shell UI
- review canvas
- task list and run view
- patch review panels
- embedded editor surface

### Desktop Main Layer

Owns:

- window lifecycle
- secure IPC boundary
- local file permission mediation
- process management
- sandbox lifecycle

### Python Sidecar Layer

Owns:

- document transforms
- patch execution
- audits
- trace updates
- manifest-aware workflows

## IPC Rule

The renderer should never directly mutate OfficeX truth layers.

The renderer must request:

- sandbox creation
- run creation
- patch preview
- patch apply
- audit execution
- export actions

through bounded IPC and runtime commands.

## Editor Role

The embedded editor is:

- a mirror surface
- a review surface
- a familiar human adjustment surface

It is not the sole source of truth.

## Sandbox Rule

Every mutable session should open a sandbox copy.

The desktop runtime should make sandbox lifecycle explicit:

- create
- bind to run
- mirror in editor
- audit
- promote or discard

## Security Rule

Desktop security should follow Electron hardening expectations:

- isolate renderer context
- avoid unrestricted node exposure
- restrict navigation
- restrict permissions
- keep provider credentials out of renderer state where practical

## Callability Rule

Embedded editor integration must remain callable from the app shell with:

- open document
- reload document
- save snapshot
- export/download candidate
- detect ready state
- detect save/dirty state

The MVP should rely only on capabilities that are realistic for the chosen
open-source editor surface.

## Migration Rule

If later parts of the runtime move to Rust, the contract above should remain
stable.

Replace internals, not the app behavior contract.
