---
doc_id: officex_macos_app_distribution_boundary
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX macOS App Distribution Boundary

## Purpose

This document defines the current macOS-first release boundary for the first
OfficeX app MVP.

It keeps the Electron shell, the Python sidecar, and future distribution work
explicit instead of implicit.

## Current App Identity

- product entry command: `officex`
- desktop shell source root: `/Users/nihao/Documents/Playground/document-ops-system/desktop`
- packaged app target name: `OfficeX.app`
- development bundle identifier target: `com.officex.desktop.dev`
- release bundle identifier target: `com.officex.desktop`

The release bundle identifier must be frozen before the first signed
distribution build.

## Debug Versus Distribution Boundary

### Local Debug Mode

Local debug mode currently means:

- `officex` launches the local Electron shell from the repo
- the Electron shell may run through `bun`
- the Python sidecar is the repo-local `.venv/bin/python`
- unsigned local builds are acceptable

### Distribution Mode

Distribution mode begins only when all of the following are true:

- bundle identifier is frozen
- packaged Electron app is produced
- signing identity is chosen
- hardened runtime policy is applied
- entitlements are frozen
- notarization input is ready

Do not present local debug behavior as if it were release-packaged behavior.

## Local Data Boundary

### Machine-Local Settings

Current default local settings root:

- `~/Library/Application Support/OfficeX`

The desktop shell may override this only through:

- `OFFICEX_SETTINGS_DIR`

Machine-local settings may include:

- workspace root
- sandbox root
- approval mode
- future renderer profile state
- future provider-state cache

These settings are not product authority files.

## Python Sidecar Boundary

In the current MVP:

- the sidecar is repo-local
- the desktop shell calls the Python CLI through bounded action plans
- renderer code must never call Python directly
- all Python execution remains mediated by Electron main plus preload IPC

The sidecar lifecycle in this phase is:

1. detect local Python runtime
2. build bounded command plan
3. execute one task
4. collect JSON/stdout/stderr
5. surface artifacts back to the app

Background daemons and always-on sidecar services are out of scope for this
phase.

## Microsoft Word Boundary

For the first app MVP:

- Microsoft Word is the primary acceptance renderer
- Word detection is required for environment readiness
- render-boundary reports must explicitly state whether Word was detected

The app may:

- detect Word
- open generated `.docx` candidates for human review

The app must not:

- depend on Word automation as the document truth layer
- treat Word as the mutation authority
- hide missing Word state during readiness checks

## Security Boundary

The desktop shell must keep these Electron rules:

- `contextIsolation` enabled
- `sandbox` enabled for renderer
- no unrestricted Node exposure in renderer
- bounded preload bridge only
- no silent provider-secret exposure into renderer state

## Signing And Entitlements Boundary

Before the first release build, OfficeX must explicitly decide:

- signing identity
- entitlements set
- hardened runtime configuration
- whether additional file-access entitlements are required

Until that point, local debug builds must be treated as unsigned developer
artifacts only.

## Notarization Readiness Boundary

Notarization work is not required for this local MVP, but readiness requires
the following to be documented before release packaging begins:

- stable bundle identifier
- stable packaged app name
- stable app resources layout
- stable sidecar inclusion strategy
- stable hardened runtime policy
- stable entitlements policy

## Current Non-Goals

This boundary document does not yet define:

- final release automation
- Apple Developer account handling
- final entitlements plist
- packaged Python sidecar embedding strategy
- non-macOS distribution
