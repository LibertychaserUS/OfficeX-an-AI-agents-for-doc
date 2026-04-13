# CURRENT_STATE

## Platform Status

- Product identity: `Document Operations System`
- Active app codename: `OfficeX`
- Internal compatibility package: `tools.report_scaffold_v3`
- Current phase: `docx` MVP runtime-surface implementation
- Current runtime posture: fresh platform-local `.venv` rebuilt on Python 3.11
  and healthy
- Current research posture: external agent-cli reference corpus established for benchmark-driven redesign
- Current document-runtime posture: official `docx`/editor reference corpus established for OOXML, editor, and workspace comparison
- Current foundation posture: domain, prompt, memory, provider, desktop-runtime,
  and release-baseline contracts are now defined as active blueprints
- Current implementation posture: first OfficeX runtime CLI layer exists with
  workspace, sandbox, task, provider, prompt, agent, and trace command families
- Current prompt posture: OfficeX cognition and role-prompt composition now
  exist as callable runtime code
- Current agent posture: machine-readable agent catalog now exists as part of
  the active runtime baseline
- Current provider posture: provider baseline catalog and provider inspection
  commands now exist as callable runtime code
- Current provider-envelope posture: dry-run provider request envelopes can now
  be assembled from provider catalogs, role prompts, and runtime task packets
- Current patch-bridge posture: OfficeX patch bundles can now be bridged into
  the deterministic revision executor for bounded paragraph-level `docx`
  mutation
- Current review-prep posture: structured manual review JSON can now be
  normalized into an OfficeX review ledger and resolved into a
  revision-compatible live anchor snapshot
- Current development-workflow posture: a dedicated development-governance
  layer now exists under `docs/development` for development memory, telemetry,
  and cross-model review without redefining product runtime authority
- Current runtime-cleanup posture: low-risk backend-runtime deduplication is
  underway and currently preserving all active OfficeX CLI/runtime contracts
- Current CLI-cleanup posture: OfficeX-facing patch command wording has been
  tightened while legacy top-level command families remain deferred for a
  separate hardening slice
- Current runtime-observability posture: `run_docx_mvp` now emits a lightweight
  run-event log beside the existing stage-history review
- Historical case context: `GU2 LoopMart` is archived, not active, and no longer used as the default CLI baseline
- Current sandbox posture: platform-owned document-edit sandbox root established for mutable session copies

## Current Priorities

- stabilize `OfficeX` docx-first MVP governance
- keep AI/program boundaries explicit for document generation and revision
- build visual-audit and review-anchor primitives before broader UI work
- wire the new domain/prompt/memory/provider/runtime contracts into the first
  executable OfficeX implementation slice
- expand the first runtime CLI slice into richer task/workspace/provider flows
- build provider request assembly and adapter logic on top of the new provider
  catalog and callable prompt runtime
- stabilize the new patch-bundle bridge before broadening into layout repair,
  figures, or richer patch scopes
- connect OfficeX review-ledger prep to future patch-bundle drafting so patch
  generation no longer depends on the old revision CLI workflow
- replace legacy-heavy revision regression coverage with OfficeX-native runtime
  tests as the new review-ledger and patch-bundle flows mature
- benchmark Codex and Claude runtime patterns before deeper runtime rewrites
- maintain a clean active-path model for daily development
- preserve compatibility while preparing future package migration
- replace remaining active-path legacy references after the neutral OfficeX baseline cutover
- keep the default recovery chain focused on OfficeX governance, not archived case context
- keep development-workflow optimization additive and separate from product
  runtime contracts
- continue backend-runtime cleanup through small, test-protected refactors
  rather than broad rewrites
- defer legacy top-level CLI command-family cleanup to a separate public-surface
  hardening stage
- keep extending OfficeX-native runtime regression coverage with realistic
  length profiles before broadening visual benchmark coverage

## Known Blockers

- None for local smoke checks

## Recent Verification

- Fresh environment created at `/Users/nihao/Documents/Playground/document-ops-system/.venv`
- `check-package`: pass
- active Python baseline set to `3.11`
- `.python-version` now tracks `3.11`
- `requirements.lock.txt` updated to keep `typer==0.23.2` compatible with the
  Python 3.11 runtime by raising `click` to `8.2.1`
- `pytest -q`: `156 passed`
- local wheel build: pass
- archived `.venv` remains historical and should not be used for active execution
- active blueprint, review-anchor protocol, visual-audit policy, editor decision,
  and issue registers were added for the current `docx` MVP
- official `docx`/editor reference repositories were cloned and indexed locally
- active default manifests were cut over from archived `GU2` inputs to the neutral
  `OfficeX` sample template and baseline
- active bootstrap, navigation, template contracts, and issue routing were
  narrowed so archived case material is no longer part of the default OfficeX
  recovery path
- sandbox and editor-compatibility blueprints were added for the `docx` MVP
- domain-agent registry, prompt-evolution protocol, memory/RAG policy,
  provider-adapter contract, desktop-runtime contract, and release-baseline
  policy were added and linked into the active governance path
- OfficeX cognition prompt layer was added and composed into role prompts
- first OfficeX runtime CLI commands were added:
  - `officex sandbox create`
  - `officex task run-docx-mvp`
- the docx MVP runtime path now writes sandbox manifests, task packets,
  candidate outputs, validation reports, candidate audits, and runtime stage
  history reports inside sandbox runs
- tests were aligned to the neutral OfficeX template profile and now pass
- prompt composition is now implemented in code via a provider-neutral prompt
  runtime module and exposed through:
  - `officex prompt show`
- provider catalog inspection is now implemented in code and exposed through:
  - `officex provider list`
  - `officex provider show`
- provider catalog is now machine-readable and tracked at:
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/provider_catalog.yml`
- workspace, task-inspection, agent-inspection, and trace-checkpoint runtime
  commands now exist:
  - `officex workspace init`
  - `officex task inspect`
  - `officex agent list`
  - `officex agent show`
  - `officex trace checkpoint`
- runtime CLI commands now expose machine-readable JSON for:
  - `officex sandbox create`
  - `officex task run-docx-mvp`
  - `officex task build-review-ledger`
  - `officex task extract-anchors`
  - `officex task apply-patch-bundle`
  - `officex prompt show`
  - `officex provider build-request`
- full runtime-surface smoke verification passed for:
  - `officex workspace init --as-json`
  - `officex prompt show --role orchestrator --as-json`
  - `officex agent list --as-json`
  - `officex agent show --agent patch_assembly_engineer --as-json`
  - `officex task run-docx-mvp --run-id cli-runtime-smoke --sandbox-root /tmp/officex-cli-smoke --as-json`
  - `officex task inspect --run-id cli-runtime-smoke --sandbox-root /tmp/officex-cli-smoke --as-json`
  - `officex trace checkpoint --trace-dir /tmp/officex-trace-smoke --as-json`
- provider request-envelope smoke verification passed for:
  - `officex task run-docx-mvp --run-id provider-envelope-smoke --sandbox-root /tmp/officex-provider-envelope-smoke --as-json`
  - `officex provider build-request --provider openai --role orchestrator --run-id provider-envelope-smoke --sandbox-root /tmp/officex-provider-envelope-smoke --config-field api_key=demo --config-field model_id=gpt-5.4 --response-contract-kind plan_object --as-json`
- OfficeX patch bridge validation passed for:
  - paragraph-level `replace_text`
  - paragraph-level `insert_paragraph`
  - paragraph-level `restyle_paragraph`
  - `officex task apply-patch-bundle --dry-run`
- OfficeX review-prep validation passed for:
  - structured manual review JSON -> OfficeX review ledger
  - paragraph exact anchor extraction
  - paragraph prefix anchor extraction
  - table-cell anchor extraction
  - `officex task build-review-ledger --as-json`
  - `officex task extract-anchors --as-json`
- agent catalog is now machine-readable and tracked at:
  - `/Users/nihao/Documents/Playground/document-ops-system/manifests/agent_catalog.yml`

## Trace State

- Local platform checkpoint baseline created: `CHECKPOINT_01`
- Local smoke verification completed after environment rebuild
- External agent-cli reference corpus recorded in `CHECKPOINT_03`
- `OfficeX` docx-first MVP blueprint and issue registers recorded in `CHECKPOINT_04`
- `docx` runtime reference corpus recorded in `CHECKPOINT_05`
- neutral `OfficeX` baseline manifests recorded in `CHECKPOINT_06`
- OfficeX sandbox/editor integration cutover recorded in `CHECKPOINT_07`
- OfficeX foundation contracts for domains, prompts, memory, providers, desktop
  runtime, and release baseline recorded in `CHECKPOINT_08`
- OfficeX runtime CLI bootstrap and cognition-layer introduction recorded in
  `CHECKPOINT_09`
- OfficeX callable prompt runtime and prompt inspection command recorded in
  `CHECKPOINT_10`
- OfficeX provider registry and provider inspection CLI recorded in
  `CHECKPOINT_11`
- OfficeX runtime CLI surface expansion and agent registry recorded in
  `CHECKPOINT_12`
- OfficeX dry-run provider request envelopes and runtime-first onboarding
  cleanup recorded in `CHECKPOINT_13`
- OfficeX patch-bundle bridge and runtime patch application surface recorded in
  `CHECKPOINT_14`
- OfficeX review-ledger and runtime anchor-prep surface recorded in
  `CHECKPOINT_15`
- OfficeX Python 3.11 baseline uplift and environment rebuild recorded in
  `CHECKPOINT_16`
- development workflow optimization documents and routing recorded in
  `CHECKPOINT_17`
- backend runtime low-risk cleanup recorded in `CHECKPOINT_18`
- backend runtime boundary tightening recorded in `CHECKPOINT_19`
- runtime length-profile regression and event logging recorded in
  `CHECKPOINT_20`
- Historical GU2 and LoopMart checkpoints remain in the archived product workspace
- Platform trace indexes should be regenerated from the local trace root only
