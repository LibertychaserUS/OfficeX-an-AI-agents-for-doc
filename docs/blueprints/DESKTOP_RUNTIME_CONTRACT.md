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

The first app MVP currently adds:

- product entry: `officex`
- local desktop-shell workspace: `/Users/nihao/Documents/Playground/document-ops-system/desktop`
- top-level actions:
  - `doctor`
  - `render-boundary`
  - controlled `docx` demo run

## Platform Priority

The first desktop target should be:

- macOS first

The desktop runtime should still preserve future portability to other systems.

## First App MVP Shape

The active frontstage shell now opens in an intake-first workbench state.

It is still not a full editing workbench and does not promote the embedded
editor to source-of-truth status.

The initial center surface remains empty until the user describes a document
task and confirms the generated task card.

The current shell therefore prioritizes:

- workspace and thread navigation
- chat-based task intake
- task confirmation card
- utility actions for `doctor`, `render-boundary`, and controlled task runs
- candidate/report viewing inside the workbench flow
- machine-local setup and readiness details as supporting, not primary, surfaces

## Architectural Split

### Renderer Layer

Owns:

- app shell UI
- intake-first workbench shell
- workspace and thread rail
- center intake/document surface
- task confirmation card presentation
- chat and utility dock
- first-launch and readiness support views
- future review canvas
- future patch review panels
- future embedded editor surface

### Desktop Main Layer

Owns:

- window lifecycle
- secure IPC boundary
- local file permission mediation
- process management
- sandbox lifecycle
- machine-local settings persistence
- sidecar command dispatch
- artifact open-path mediation

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

- machine readiness checks
- renderer boundary checks
- sandbox creation
- run creation
- patch preview
- patch apply
- audit execution
- export actions

through bounded IPC and runtime commands.

The current first-app actions should remain bounded to:

- `doctor`
- `render-boundary`
- `run-docx-demo`

They should not expose arbitrary shell execution to the renderer.

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

## Machine-Local Settings Rule

The first app MVP must keep setup state outside product authority files.

Machine-local settings currently include:

- default workspace root
- default sandbox root
- default approval mode
- detected local readiness state

These belong under the local OfficeX settings directory, not in committed
product manifests.

## First-Launch Rule

The first-launch path should stay narrow and explicit.

It may configure:

- workspace root
- sandbox root
- approval mode
- provider presence detection
- Word detection

It should not silently rewrite product governance files.

## Security Rule

Desktop security should follow Electron hardening expectations:

- isolate renderer context
- avoid unrestricted node exposure
- restrict navigation
- restrict permissions
- keep provider credentials out of renderer state where practical
- keep file opens and command dispatch behind preload IPC only
- avoid direct renderer writes to candidate or authority paths

## Renderer Acceptance Rule

The phase-1 acceptance renderer is:

- `Microsoft Word`

`render-boundary` should therefore measure real environment behavior against
Word first, rather than treating the embedded editor as the acceptance source.

## macOS Release Boundary

The current Electron shell is a local-development MVP, not a distribution-ready
artifact.

Before signed distribution claims, the desktop layer must explicitly define and
verify:

- bundle identifier
- debug-vs-distribution boundary
- hardened runtime posture
- entitlements
- nested-code signing
- notarization readiness
- Python sidecar packaging boundary

Until those are cut and verified, the shell should be described as local app
MVP infrastructure only.

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
