# Engineering Issues Register

## Purpose

This is the living register for:

- blockers
- failures
- resolved incidents
- future risk clusters
- iteration directions

Update this file whenever a real issue is reproduced, resolved, deferred, or
promoted into roadmap work.

## Current Status

- Platform-local smoke environment: healthy
- Local smoke result:
  - `check-package`: pass
  - `pytest -q`: `168 passed`
  - `desktop/bun run check`: pass
  - local wheel build: pass
- Active platform root:
  - `/Users/nihao/Documents/Playground/document-ops-system`
- External historical archive root:
  - `/Users/nihao/Documents/LegacyArchives/gu2-loopmart-outside-playground`

## Active Blockers

- None for local platform smoke checks

## Resolved Incidents

### DOS-001 Archived venv unusable for current smoke checks

- Status: resolved by replacement, not by repair
- Scope: historical archived environment only
- Symptom:
  - platform CLI preflight failed during imports
  - `PIL/_imaging.cpython-39-darwin.so` failed to load
  - `liblzma.5.dylib` was rejected by system policy
- Root cause:
  - the archived `.venv` contained Pillow native libraries that macOS would not
    load in the current environment
- Resolution:
  - created a fresh local environment at
    `/Users/nihao/Documents/Playground/document-ops-system/.venv`
  - reinstalled platform dependencies there
- Policy:
  - do not treat archived virtual environments as active runtime dependencies

### DOS-002 Homebrew Python runtime blocked by system policy

- Status: bypassed
- Symptom:
  - `/opt/homebrew/bin/python3` failed before use
  - Python framework load was denied by system policy
- Root cause:
  - the local Homebrew Python installation is not currently safe to rely on
    for this workspace
- Resolution:
  - used `/usr/bin/python3` to build the fresh platform-local environment
- Policy:
  - prefer the platform-local `.venv` once created
  - do not assume Homebrew Python is healthy on this machine

### DOS-003 Fresh environment failed wheel-based packaging smoke

- Status: resolved
- Symptom:
  - wheel build test failed with `invalid command 'bdist_wheel'`
- Root cause:
  - fresh `.venv` did not include wheel build tooling
  - `setuptools` was also below the build-system floor implied by the project
    metadata
- Resolution:
  - added `setuptools==80.9.0`
  - added `wheel==0.45.1`
  - updated the local environment
- Prevention:
  - keep build tooling present in the environment lock used for smoke setup

### DOS-004 Test suite still contained legacy product strings

- Status: resolved
- Symptom:
  - tests still expected `LoopMart Report Scaffold V3`
  - tests still expected `Scaffold Placeholder`
  - tests still referenced old report-oriented wording
- Root cause:
  - product identity and fixtures were updated, but several assertions still
    encoded the old naming
- Resolution:
  - updated tests to assert the current platform identity:
    - `Document Operations System`
    - `Platform Writer Demo`
    - `Platform Placeholder`
- Prevention:
  - when product identity changes, update fixtures and tests in the same change

### DOS-005 Desktop settings tests wrote to the real user Library path

- Status: resolved
- Symptom:
  - `desktop/bun run check` failed under sandboxed execution
  - `src/tests/settingsStore.test.ts` attempted to create
    `/Users/nihao/Library/Application Support/OfficeX`
- Root cause:
  - the desktop settings layer depended on an import-time home-path constant
  - Bun test module loading allowed `actionPlans` to be loaded before the test
    mock, so the test hit the real machine path instead of an isolated temp
    path
- Resolution:
  - switched the desktop settings path to a runtime resolver using
    `OFFICEX_SETTINGS_DIR`
  - updated the desktop settings tests to use an isolated temp settings
    directory through the environment instead of a brittle module mock
- Prevention:
  - keep machine-local paths runtime-resolved rather than import-time frozen
  - prefer environment-based test isolation for desktop local-state code

### CASE-003 Cross-renderer document stability

- Status: unresolved as a platform capability
- Scope: product-wide future requirement
- Symptom pattern:
  - document appearance varied across editors and renderers
  - manual stable copies were sometimes more reliable than later aligned
    candidates
- Impact:
  - document correctness is not equivalent to renderer stability
- Needed capability:
  - explicit cross-renderer validation matrix

## Open Risk Clusters

### RISK-001 Compatibility package name drift

- Current state:
  - product name is `Document Operations System`
  - internal package remains `tools.report_scaffold_v3`
- Risk:
  - future contributors may confuse product identity with technical legacy name
- Mitigation:
  - keep active-path and package-contract docs explicit
  - do package rename only as a dedicated migration

### RISK-002 Archive boundary violations

- Current state:
  - historical materials live outside the active OfficeX repository
- Risk:
  - future work may accidentally edit archived material or reuse archived
    runtime assets
- Mitigation:
  - treat archived workspaces as read-only by default
  - keep all active execution in the platform root

### RISK-003 Environment reproducibility gaps

- Current state:
  - a fresh `.venv` now works
- Risk:
  - future rebuilds may fail if build tooling is omitted or if machine-local
    Python assumptions change
- Mitigation:
  - keep environment setup documented
  - verify smoke checks after dependency changes

### RISK-004 Path confusion during context recovery

- Current state:
  - platform and archived case study now have separate trace roots
- Risk:
  - operators may resume from archived trace instead of platform trace
- Mitigation:
  - keep [ACTIVE_RULES_AND_PATHS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md)
    and replay docs current

## Iteration Directions

These are not detailed plans. They are tracked directions that can later be
expanded into real product branches or research tracks.

### ITER-001 Durable environment bootstrap

- Goal:
  - make environment creation deterministic and one-command
- Candidate outcomes:
  - bootstrap script
  - explicit local toolchain checks
  - clearer smoke bootstrap in README

### ITER-002 Cross-renderer validation

- Goal:
  - verify that generated or revised documents are stable across renderers
- Candidate outcomes:
  - renderer matrix
  - visual diff lane
  - render-audit expansion beyond layout heuristics

### ITER-003 Compatibility package migration

- Goal:
  - eventually retire `tools.report_scaffold_v3`
- Candidate outcomes:
  - dedicated rename release
  - import-compat shim
  - updated package contract and tests

### ITER-004 Document IR and provenance

- Goal:
  - separate document semantics from final file format mechanics
- Candidate outcomes:
  - unified intermediate representation
  - provenance-aware transforms
  - richer review and diff tooling

### ITER-005 Review memory and compliance profiles

- Goal:
  - turn repeated human review patterns into reusable platform behavior
- Candidate outcomes:
  - learned review preferences
  - schema-driven compliance profiles
  - profile-aware audit harnesses

## Update Rules

- Add an entry only when there is a concrete symptom, failure, or decision.
- Mark incidents as `resolved`, `bypassed`, `deferred`, or `active`.
- Keep archived-case issues separate from active platform blockers.
- Promote mature iteration directions into
  [PRODUCT_ROADMAP.md](/Users/nihao/Documents/Playground/document-ops-system/docs/PRODUCT_ROADMAP.md)
  when they become committed work.
