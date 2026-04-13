---
doc_id: backend_runtime_review_register
layer: register
authority: active
status: living
owner: platform_engineering
machine_source_of_truth: false
---

# Backend Runtime Review Register

## Scope

This register records backend runtime review findings for the active `OfficeX`
`docx` runtime.

It focuses on:

- runtime service boundaries
- deterministic mutation flow
- provider/task/review/patch layering
- operational safety and auditability
- usability for the future app shell

It does not yet review frontend/Electron implementation because there is no
active frontend codebase in the live root.

## Review Standard

This review uses three standards:

1. OfficeX-specific requirements
   - deterministic `docx` mutation
   - replayable trace
   - `platform truth + Office mirror`
   - explicit human approval on risky actions
2. Agent-runtime design patterns from official docs
   - isolated task environments and evidence-backed review from [OpenAI Codex](https://openai.com/index/introducing-codex/)
   - subagent specialization, scoped tools, and independent permissions from [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
   - session, handoff, and guardrail patterns from the [OpenAI Agents SDK Sessions](https://openai.github.io/openai-agents-python/sessions/), [Handoffs](https://openai.github.io/openai-agents-python/handoffs/), and [Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
   - durable execution and HITL patterns from [LangGraph durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution) and [LangChain human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
3. Pragmatic backend engineering rules
   - stable contracts
   - narrow mutation authority
   - observability
   - resumability
   - low coupling
   - testability

## Current Strengths

- The runtime already has a meaningful public surface:
  - `workspace`
  - `sandbox`
  - `task`
  - `provider`
  - `agent`
  - `trace`
- The OfficeX path is now genuinely task-oriented rather than only
  baseline/build/validate oriented.
- Mutation authority is narrow and defensible:
  - provider output is dry-run only
  - patch bundles are bounded
  - the revision executor remains the only mutation engine
- The review-prep path is structurally correct:
  - review findings JSON
  - review ledger
  - live anchor snapshot
  - patch bundle
  - deterministic executor
- Runtime outputs are already machine-readable enough for a future app shell.
- Trace and checkpoint discipline exists and is actively used.

## Priority Findings

### P1: `run_docx_mvp()` is too monolithic

- Path: [officex_runtime.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/officex_runtime.py)
- Problem:
  one function currently owns sandbox creation, source staging, task packet
  construction, build execution, candidate audit, validation, and stage-history
  generation.
- Risk:
  this makes the main runtime path harder to reuse, harder to debug by stage,
  and harder to evolve into resumable app-driven workflows.
- Why this matters:
  Codex-style isolated tasks and LangGraph-style resumability both benefit from
  explicit stage boundaries, not one large orchestration function.
- Recommendation:
  split into thin orchestration plus stage services:
  - sandbox prep
  - task packet emit
  - deterministic build
  - audit
  - validation
  - run-summary emit

### P1: task-packet loading still leaks through the wrong service boundary

- Paths:
  - [provider_runtime.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/provider_runtime.py)
  - [officex_runtime.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/officex_runtime.py)
- Problem:
  provider runtime currently imports task-packet loading from `officex_runtime`.
- Risk:
  this couples the provider layer to one specific task-runner module instead of
  a neutral runtime state/service layer.
- Recommendation:
  move task-packet resolution into a neutral runtime service module such as:
  - `task_runtime.py`
  - or shared `runtime_common.py`

### P1: OfficeX public runtime is still partially constrained by the legacy revision world

- Paths:
  - [review_runtime.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/review_runtime.py)
  - [patch_bridge_runtime.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/patch_bridge_runtime.py)
  - [revision](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/revision)
- Problem:
  the deterministic mutation backend is correct, but the surrounding runtime
  still inherits issue-ledger assumptions, anchor record shapes, and revision
  naming from the old compatibility lane.
- Risk:
  new public OfficeX contracts can drift toward legacy semantics if this is not
  kept explicit.
- Recommendation:
  keep reusing the executor, but progressively wrap it behind OfficeX-native
  contracts and replace legacy-heavy tests with OfficeX-native runtime tests.

### P1: tool-call and adapter guardrails are not yet implemented as runtime policy

- Current state:
  provider envelopes exist, but real adapter dispatch, tool-call validation, and
  tool guardrail policy do not.
- Risk:
  once live provider dispatch is introduced, OfficeX could let model-side tool
  outputs bypass deterministic validation unless the policy is formalized first.
- Recommendation:
  add a backend `tool_guardrail` layer before live provider dispatch:
  - validate requested tool/action against policy
  - validate required fields
  - reject unsafe scope
  - record decision in run artifacts

### P1: run artifacts do not yet snapshot enough versioned authority

- Problem:
  run outputs do not yet consistently stamp:
  - prompt pack version
  - agent catalog version
  - provider catalog version
  - rule/ledger schema version
- Risk:
  replay is weaker than it should be, because future drift can change the meaning
  of a run without a crisp version boundary.
- Recommendation:
  add a runtime `authority snapshot` block to task packets and run reports.

## Secondary Findings

### P2: runtime duplication exists and should be consolidated carefully

- Confirmed duplicate patterns:
  - ID normalization
  - structured JSON/YAML loading with schema wrapping
  - mutable candidate path guarding
  - sandbox-aware artifact dir resolution
  - workspace/sandbox manifest emission
- Recommendation:
  continue consolidating these into a shared runtime utility layer, but keep the
  public behavior stable and avoid over-abstracting domain logic.

### P2: workspace and sandbox creation are conceptually similar but not yet modeled as one pattern

- Paths:
  - [workspace_runtime.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/workspace_runtime.py)
  - [officex_runtime.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/officex_runtime.py)
- Risk:
  drift in directory layout, manifest naming, and metadata rules.
- Recommendation:
  share the bootstrap mechanics, but keep distinct models for workspace and
  sandbox semantics.

### P2: observability is still mostly checkpoint-oriented, not run-oriented

- Current state:
  checkpoints and markdown reports are good, but there is no dedicated
  structured run-event log.
- Risk:
  debugging multi-stage runtime failures will become harder once real provider
  dispatch and app orchestration exist.
- Recommendation:
  add a lightweight run-event log with:
  - stage start
  - stage finish
  - error
  - approval decision
  - emitted artifact paths

### P2: runtime resume semantics are still weak

- Current state:
  a run can be inspected, but task execution is still mostly one-shot.
- Risk:
  the runtime is not yet aligned with durable-execution patterns where a failed
  or interrupted stage can resume without rebuilding everything.
- Recommendation:
  formalize stage-level state and resumable checkpoints inside sandboxes.

### P2: provider layer is generic, but not yet operationally complete

- Good:
  the request envelope shape is stable and provider-neutral.
- Missing:
  - config source policy
  - secure secret resolution policy
  - retry/backoff classification
  - live adapter contract
  - adapter result validation
- Recommendation:
  keep this as the next provider slice, but only after tool-guardrail policy is
  defined.

## Desirable Additions For Better Usability

### Must-add next

- `task_runtime` or equivalent neutral runtime-state service
- tool guardrail policy before live provider dispatch
- authority snapshot metadata in run artifacts
- OfficeX-native runtime tests for:
  - review ledger
  - anchor prep
  - patch bundle
  - patch bridge
  - sandbox lifecycle
- structured run-event logging

### Should-add soon

- resumable stage execution inside sandbox runs
- sandbox lock or active-run coordination
- stronger error taxonomy for CLI/app consumption
- explicit runtime health/status command

### Defer

- distributed session storage
- multi-document orchestration
- advanced queue/worker model
- broad patch scope for figures/layout/text boxes

## Testing Direction

The current backend should move toward this test split:

- OfficeX-native runtime tests as the main validation layer
- deterministic executor unit tests
- a thin legacy revision compatibility lane

The legacy lane should remain only to protect the migration boundary. It should
not dominate the active runtime test surface.

## Suggested Next Engineering Order

1. complete low-risk runtime deduplication
2. extract neutral task runtime services
3. add run-event logging and authority snapshots
4. define tool guardrail policy
5. replace legacy-heavy tests with OfficeX-native runtime coverage
6. only then introduce live provider adapters
