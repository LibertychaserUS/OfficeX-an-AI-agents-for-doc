---
doc_id: development_history_review_register
layer: register
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Development History Review Register

## Purpose

This register summarizes major OfficeX development-stage retrospectives and the
lessons that should continue shaping implementation.

Detailed history remains in local checkpoints.

## Current Entries

### Stage: Foundation Reframe

- status: active history
- scope:
  - OfficeX identity cutover
  - active-path de-GU2 cleanup
  - blueprint and contract expansion
- what worked:
  - active manifests were successfully detached from GU2 defaults
  - reference corpora were separated from active platform code
  - memory, provider, desktop, and agent contracts are now explicit
- what failed or was misread:
  - old CLI structure was kept too close to the report-scaffold mental model
  - some early stage-review output was aimed at runtime runs rather than
    OfficeX engineering-stage reflection
- carry forward:
  - keep archive/reference layers separate from active governance
  - treat OfficeX as a runtime, not as a document editor wrapper
  - keep RAG below authoritative memory
  - continue replacing old scaffold workflow assumptions with runtime-first
    contracts

### Stage: Runtime CLI Bootstrap

- status: active history
- scope:
  - first OfficeX runtime CLI layer
  - sandbox lifecycle entrypoint
  - docx MVP task-run entrypoint
  - prompt cognition layering
- what worked:
  - old deterministic primitives were reusable as a lower tool layer
  - `officex sandbox create` and `officex task run-docx-mvp` now form the first
    task-oriented runtime entry
  - prompt cognition was added as a provider-neutral composition layer instead
    of being pushed into root constraints
- what failed or was misread:
  - one early interpretation confused runtime stage review with OfficeX
    engineering-stage retrospective
  - a few tests still reflected pre-OfficeX template assumptions and had to be
    aligned to the neutral baseline
- carry forward:
  - continue treating old CLI commands as internal primitives rather than the
    future user-facing command model
  - keep development retrospectives separate from per-run runtime reports
  - align template manifests and tests whenever the neutral OfficeX baseline
    changes

### Stage: Prompt Runtime Bootstrap

- status: active history
- scope:
  - provider-neutral cognition file
  - callable prompt composition layer
  - runtime CLI prompt inspection command
- what worked:
  - cognition was separated from root constraints and project governance
  - prompt composition is now a real code path instead of a manual convention
  - role prompts can now be rendered with or without the OfficeX cognition
    layer
- what failed or was misread:
  - an earlier edit briefly tried to solve this through `AGENTS.md`, which was
    the wrong layer and had to be avoided
- carry forward:
  - keep provider-facing cognition in prompt packs, not governance files
  - keep role/domain prompt composition explicit and testable
  - build API provider integration on top of this callable prompt layer rather
    than reintroducing ad hoc prompt assembly

### Stage: Provider Registry Bootstrap

- status: active history
- scope:
  - machine-readable provider catalog
  - provider prompt binding runtime
  - provider inspection CLI surface
- what worked:
  - provider baselines are now file-backed and versionable instead of implicit
    notes in blueprints
  - provider inspection is now executable through runtime commands rather than
    manual prompt assembly
  - the provider layer stays decoupled from deterministic `docx` mutation
- what failed or was misread:
  - provider handling had remained only as documentation, which left the runtime
    without a machine-readable contract
- carry forward:
  - keep provider catalogs authoritative and keep secrets out of repo-tracked
    manifests
  - expand provider adapters on top of this registry instead of coupling models
    directly into task commands
  - benchmark new providers before allowing them into authoritative document
    workflows

### Stage: Runtime CLI Surface Expansion

- status: active history
- scope:
  - `workspace / task / agent / trace` OfficeX runtime commands
  - machine-readable agent catalog exposure
  - runtime-facing JSON command contracts
- what worked:
  - the CLI surface now maps to OfficeX runtime concepts instead of only
    baseline/build/validate primitives
  - `task inspect` was pulled behind a runtime helper instead of leaving packet
    path resolution in the CLI command layer
  - smoke coverage now exercises workspace creation, sandbox creation, prompt
    inspection, provider inspection, agent inspection, runtime task execution,
    and trace checkpoint creation
- what failed or was misread:
  - early tests missed error handling around duplicate workspace creation
  - old scaffold wording remained in a few CLI outputs and had to be cleaned up
  - runtime command JSON contracts were incomplete until `sandbox`, `task`, and
    `prompt` commands exposed `--as-json`
- carry forward:
  - keep old deterministic commands as internal primitives rather than user
    workflow entrypoints
  - keep runtime command IO stable enough for the future Electron/TS app shell
  - continue replacing lingering scaffold semantics with OfficeX runtime
    language as the public surface expands

### Stage: Provider Request Envelope Bootstrap

- status: active history
- scope:
  - dry-run provider request assembly layer
  - provider-facing task-packet binding
  - runtime CLI envelope export surface
- what worked:
  - provider catalog, prompt runtime, and task packets are now bound into one
    stable envelope object instead of remaining separate contracts
  - config-field parsing and validation are now explicit and testable without
    storing secrets in repo-tracked state
  - active onboarding docs now point at the OfficeX runtime surface instead of
    defaulting back to the old baseline/build workflow
- what failed or was misread:
  - the existing provider catalog did not explicitly separate required config
    inputs from optional ones, so the dry-run layer had to derive required
    fields conservatively
  - runtime-facing docs still contained legacy entrypoint bias until this slice
    cleaned the resume and README paths
- carry forward:
  - keep request envelopes generic and provider-neutral until real adapter
    dispatch is introduced
  - keep config validation separate from secret storage and environment policy
  - use this envelope contract as the only handoff shape for future Electron
    app calls and adapter execution

### Stage: Patch Bridge Bootstrap

- status: active history
- scope:
  - OfficeX patch bundle contract
  - OfficeX-to-revision bridge runtime
  - runtime patch application CLI surface
- what worked:
  - the patch path now reuses the existing deterministic revision executor
    instead of introducing a second direct `docx` mutation engine
  - paragraph-level `replace_text`, `insert_paragraph`, and
    `restyle_paragraph` are now executable through one bounded OfficeX runtime
    command
  - the bridge rejects unsupported operation kinds, unsupported scope,
    non-unique anchors, immutable imports, archived targets, and candidate hash
    drift before mutation starts
- what failed or was misread:
  - the original OfficeX patch schema was broader than the actual safe MVP
    execution subset, so the bridge had to narrow the executable contract
    explicitly
  - the existing revision stack assumes an issue-ledger-shaped world, so the
    bridge had to map OfficeX operations onto anchor-backed revision issue ids
    rather than inventing a parallel low-level executor
- carry forward:
  - keep patch bundles provider-neutral and keep providers out of deterministic
    mutation
  - expand patch scope only after paragraph-level text/style mutations remain
    stable under regression
  - continue treating anchors and candidate hashes as hard execution authority,
    not advisory metadata

### Stage: Review Ledger And Runtime Anchor Prep

- status: active history
- scope:
  - OfficeX review-ledger contract
  - structured manual review JSON normalization
  - runtime anchor extraction surface
- what worked:
  - review findings now have a public OfficeX prep contract instead of relying
    on the old revision issue-ledger shape
  - the new review runtime reuses the existing deterministic anchor extractor
    logic while removing the hard dependency on revision issue profiles
  - paragraph exact, paragraph prefix, and table-cell anchor extraction are now
    callable through OfficeX runtime commands and remain compatible with the
    existing patch bridge
- what failed or was misread:
  - the first union-based anchor-rule model used Python 3.10-style `|` syntax
    and had to be corrected for the then-active Python 3.9 runtime before the
    later Python 3.11 baseline uplift
  - the old anchor extractor was too tightly coupled to issue-profile lookup,
    so a generic rule-based extraction helper had to be introduced before the
    OfficeX runtime could reuse it cleanly

### Stage: Desktop Startup Truth Recovery

- status: active history
- scope:
  - OfficeX app empty-shell incident
  - preload bootstrap failure diagnosis
  - desktop startup observability hardening
- what worked:
  - real Electron logs were collected instead of trusting `typecheck` and build
    success as evidence of product readiness
  - the app was verified through the real product surface, not only through CLI
    smoke commands
  - preload-format and preload-path issues were narrowed quickly once startup
    logs were allowed to speak
- what failed or was misread:
  - earlier work treated a passing `bun run check` as too close to “desktop
    shell is fine,” which hid the real startup defect
  - renderer failures could previously degrade into a blank window with no
    user-facing explanation
  - desktop action/execution types were expanded before the implementation was
    fully brought back into contract, which temporarily left the shell in a
    type-drift state
- carry forward:
  - do not accept build success as proof of product-entry readiness
  - keep startup diagnostics and visible renderer failure states in place as a
    permanent desktop baseline
  - whenever the desktop surface changes, verify at least one real in-app
    action rather than stopping at static checks
- carry forward:
  - keep free-text review parsing and rubric compilation out of the runtime
    until the structured review-ledger contract is stable
  - use the OfficeX review-ledger as the only new prep contract above the old
    revision compatibility layer
  - next connect review-ledger prep to patch-bundle drafting so OfficeX can
    generate bounded patch bundles without going back through the legacy
    revision CLI

### Stage: Python 3.11 Runtime Baseline Uplift

- status: active history
- scope:
  - rebuild the active `.venv` on Homebrew `python@3.11`
  - raise the declared OfficeX Python floor
  - repair lockfile and test drift exposed by the runtime change
- what worked:
  - the accidental fallback to CommandLineTools Python 3.9.6 was traced to an
    overly generic `python3 -m venv` workflow plus a wide `>=3.9` package floor
  - OfficeX now has an explicit `3.11` baseline via `pyproject.toml`,
    `README.md`, and `.python-version`
  - `check-package` now performs real runtime/package integrity checks instead
    of returning a placeholder success message
- what failed or was misread:
  - the existing lockfile pinned `click==8.1.8`, which is incompatible with
    `typer==0.23.2` on Python 3.11 and had to be corrected
  - one test fixture change incorrectly pushed the new Python baseline into the
    legacy `REV-*` compatibility lane, which broke old anchor matching and had
    to be rolled back
- carry forward:
  - keep the OfficeX active baseline explicit and versioned; do not rely on
    whichever `python3` happens to be first on PATH
  - treat legacy revision fixtures as compatibility coverage, not as the public
    OfficeX contract
  - replace legacy-heavy revision tests with OfficeX-native runtime tests as
    the public review-ledger, anchor-prep, and patch-bundle flows stabilize
  - continue using runtime upgrades to expose stale dependency pins and weak
    test assumptions early

### Stage: Backend Runtime Review

- status: active history
- scope:
  - runtime service boundaries
  - duplication and coupling audit
  - usability and operability review for the backend runtime
- what worked:
  - the active runtime already has defensible public concepts: workspace,
    sandbox, task, provider, review, patch, and trace
  - mutation authority remains narrow because deterministic patch execution is
    still the only real write path
  - the provider envelope, review ledger, and patch bridge contracts are good
    foundations for a future app shell
- what failed or was misread:
  - too much orchestration still sits inside large service functions instead of
    being split into reusable stage services
  - the provider layer still reaches into the task runner through the wrong
    module boundary
  - legacy revision semantics are still too visible around the active OfficeX
    runtime
- carry forward:
  - keep low-risk deduplication focused on shared runtime primitives, not broad
    rewrites
  - add run-event logging, authority snapshots, and tool guardrails before live
    provider dispatch
  - move the main test surface toward OfficeX-native runtime behavior rather
    than legacy revision fixtures

### Stage: App MVP Readiness Hardening

- status: active history
- scope:
  - doctor/report persistence
  - desktop readiness gating
  - product-entry invocation hardening
- what worked:
  - `doctor` and `render-boundary` now leave behind stable JSON/Markdown
    evidence instead of ephemeral terminal output
  - desktop readiness is now anchored to a real matching `doctor` result for
    the current workspace/sandbox pair
  - the desktop sidecar path now calls `product_entry` directly, preserving the
    product-facing surface instead of binding the app to the raw CLI root
- what failed or was misread:
  - the first desktop bootstrap treated Python detection as equivalent to
    product readiness, which was too optimistic
  - switching the desktop shell onto
    `python -m tools.report_scaffold_v3.product_entry` exposed that the module
    lacked a `__main__` entry and therefore did nothing when launched that way
  - sandboxed verification in Codex cannot write to
    `~/Library/Application Support/OfficeX`, so local smoke required
    `OFFICEX_SETTINGS_DIR=/tmp/...` during validation
- carry forward:
  - keep machine-local diagnostics file-backed and reopenable from the app
  - do not mark the product ready unless the latest matching `doctor` result
    passes the core checks
  - keep product entry and raw legacy CLI invocation paths distinct

### Stage: Development Workflow Optimization Layer

- status: active history
- scope:
  - add a development-only governance layer inspired by external agent-workflow
    best practices
  - keep development-memory, review-pack, telemetry, and cross-model critique
    rules separate from the OfficeX product runtime
  - route these rules through active indexes without rewriting root governance
    or product runtime contracts
- what worked:
  - a clean `docs/development` section now exists for development-memory
    layering, command/agent/knowledge-pack structure, telemetry/hotspot rules,
    and cross-model review
  - `CONSTRAINT_INDEX.md` and `ACTIVE_RULES_AND_PATHS.md` now point to this new
    layer explicitly and state that it governs how OfficeX is built, not how
    OfficeX runtime executes document tasks
  - external reference patterns such as layered memory, critique lanes, and
    telemetry-based hotspot review can now be adopted without polluting
    authoritative runtime memory
- what failed or was misread:
  - the initial user concern was valid: without an explicit boundary, these
    improvements could easily be mistaken for a mandate to rewrite root
    constraints, all MD governance, and the harness catalog
  - development workflow optimization and product runtime optimization were too
    easy to conflate before the dedicated development layer existed
- carry forward:
  - keep development workflow improvements additive and scoped; do not rewrite
    root governance unless a cross-project safety problem actually exists
  - do not let development telemetry, review notes, or critique-pack output
    silently modify authoritative OfficeX runtime contracts
  - use this layer to improve how OfficeX is engineered, reviewed, and evolved,
    while leaving product runtime authority in the existing blueprint,
    manifest, and trace system

### Stage: Backend Runtime Low-Risk Cleanup

- status: active history
- scope:
  - reduce low-value duplication inside the active OfficeX backend runtime
  - keep runtime behavior, public contracts, and product authority unchanged
  - tighten the boundary between runtime services and revision compatibility
    helpers
- what worked:
  - `run_docx_mvp` was split into clearer internal stage helpers instead of
    keeping task-packet creation, stage-history composition, and severity
    counting inline in one large flow
  - review-prep and patch-bridge runtime paths now use runtime-owned write
    helpers instead of reaching back into revision write helpers for ordinary
    runtime artifact output
  - task-packet loading restored a stable OfficeX-facing schema error message
    after generic model-name leakage appeared during refactoring
- what failed or was misread:
  - a first-pass refactor changed one CLI-visible schema error message and was
    caught immediately by runtime-surface tests
  - there is still meaningful structural work left; this slice only cleaned the
    safest duplication and boundary leaks
- carry forward:
  - continue preferring low-risk refactors that preserve public runtime
    contracts and smoke behavior
  - keep replacing revision-surface leakage with runtime-owned helpers only
    when the behavioral boundary is already clear
  - leave larger service-splitting and event-log work for a dedicated runtime
    hardening slice rather than mixing it into feature implementation

### Stage: Backend Runtime Boundary Tightening

- status: active history
- scope:
  - continue backend-runtime cleanup after the first low-risk slice
  - tighten internal validation and provider-resolution boundaries
  - reduce obvious OfficeX-facing revision wording leakage without changing
    JSON contracts or file-layout contracts
- what worked:
  - patch-bridge validation now reuses the already-computed candidate hash
    instead of re-hashing the candidate file once per operation
  - provider runtime now resolves provider entry, model, prompt, and notes
    through one internal context helper instead of duplicating the same lookup
    chain across multiple functions
  - OfficeX patch command wording now speaks in terms of the patch bridge
    rather than the revision executor while still keeping legacy-compatible JSON
    field names intact
- what failed or was misread:
  - the main remaining CLI cleanliness problem is still structural: legacy
    top-level command families remain public even though the OfficeX runtime
    surface is now the preferred path
  - that larger CLI cleanup should not be mixed into low-risk backend cleanup
    because it changes discoverability and public help surfaces
- carry forward:
  - keep using subagent critique for low-cost architecture and CLI-surface
    review before larger cleanup decisions
  - defer removal or hiding of legacy command families to a dedicated CLI
    surface hardening stage
  - continue keeping human-readable OfficeX surfaces clean while preserving
    machine-readable compatibility until the package migration is deliberate

### Stage: Runtime Length Profile Regression And Event Logging

- status: active history
- scope:
  - add OfficeX-native runtime regression coverage for short, medium, long, and
    ultra-long build-source profiles
  - add lightweight run-event logging to the `docx` MVP runtime without
    changing the public run-summary contract
- what worked:
  - a new OfficeX runtime test file now exercises four length profiles through
    the active `run_docx_mvp` path and one CLI long-profile path
  - the runtime now writes `run_event_log.json` and `run_event_log.md` alongside
    the existing stage-history review so execution stages are easier to debug
    without changing JSON response contracts
  - the new tests increased the full suite from 156 to 161 passing tests while
    staying on the OfficeX runtime surface rather than the legacy revision lane
- what failed or was misread:
  - nothing functional regressed in this slice; the main caution remains that
    length-profile coverage is structural and runtime-oriented, not a substitute
    for future visual/render stress benchmarks
- carry forward:
  - keep adding OfficeX-native regression files around realistic runtime
    profiles instead of expanding legacy revision fixtures
  - build on the new run-event log for future runtime observability rather than
    inventing a second ad hoc reporting lane
  - add larger document and visual stress benchmarks separately when the render
    audit lane is ready

### Stage: Provider Prompt Compiler Structure

- status: active history
- scope:
  - replace opaque provider prompt concatenation with a first explicit prompt
    compiler shape
  - emit prompt manifest refs, resolved prompt refs, compiled prompt debug, and
    prompt trace metadata through provider bindings and request envelopes
  - make human-readable provider output show prompt layers rather than only one
    undifferentiated prompt blob
- what worked:
  - provider prompt assembly now keeps the compiled prompt as a debug artifact
    while exposing refs and hashes for audit and future narrowing
  - the provider request envelope remains backward-compatible through
    `system_prompt`, but now also carries prompt manifest, resolved refs, and a
    prompt trace record
  - the old `check-outline` CLI output regression was fixed during this slice,
    bringing the full suite back to green
- what failed or was misread:
  - the provider layer is still not a full DSL; this slice introduces the
    compiler shape, but imports remain markdown-file level rather than
    section-level rule imports
  - the CLI is still an operator/runtime surface, not an interactive product
    shell; this slice clarified that but did not change the overall CLI product
    posture
- carry forward:
  - narrow prompt refs from whole markdown files to section-level imports
  - add provider-targeted compile passes instead of one universal compiled
    prompt output
  - keep compiled prompt text available for debug, but treat prompt manifests
    and trace records as the real long-term authority shape

### Stage: First App MVP Product Entry And Desktop Shell

- status: active history
- scope:
  - cut a real `officex` product entry instead of relying only on Python module
    paths
  - add `doctor` and `render-boundary` as first-class OfficeX product actions
  - scaffold the first Electron+Bun macOS shell with a readiness-first home
  - keep settings machine-local and out of product authority files
- what worked:
  - the new `officex` entry now routes to the desktop shell and exposes
    `doctor`, `render-boundary`, and `runtime ...` on the product-facing path
  - `officex doctor` now checks Python/package integrity, Bun, desktop shell,
    Word, workspace/sandbox writability, provider state, and a smoke run
  - `officex render-boundary` now produces a Word-first capability matrix over
    short, medium, long, and ultra-long scenarios
  - the new `desktop/` shell builds and tests locally, and its actions map back
    into the active OfficeX runtime rather than inventing a second backend lane
  - desktop settings persistence was corrected to use a machine-local override
    path in tests rather than writing into the real user Library path
- what failed or was misread:
  - the first desktop-shell test pass from the isolated implementation lane did
    not hold under the full local Bun run because the settings directory logic
    still froze the real user path too early
  - that failure was not architectural; it was a runtime-boundary bug caused by
    constant-path resolution instead of call-time path resolution
  - the app shell is still local-development infrastructure, not a signed or
    notarization-ready macOS distribution artifact
- carry forward:
  - keep the first app MVP narrow around readiness, boundary evidence, and one
    controlled `docx` task before expanding into a heavier workbench
  - define bundle id, entitlements, hardened runtime, and notarization posture
    before making macOS distribution claims
  - expand render-boundary scenario coverage before presenting paragraph-level
    results as a broader editing guarantee

## Update Rule

When a major stage closes, append a new entry here and point to the matching
checkpoint.
