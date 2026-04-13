---
doc_id: officex_agent_call_contract
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Agent Call Contract

## Purpose

OfficeX is a hybrid system.

Its moat includes:

- AI agents for planning, text, review, and proposal
- deterministic runtime services for execution, validation, and mutation

This contract prevents duplicated authority and unclear routing.

## Role Split

### AI Agents

May:

- interpret tasks
- draft text
- generate review findings
- generate patch proposals
- draft image or chart generation code

May not:

- become final mutation authority
- declare unresolved claims as verified
- bypass approval gates

### Runtime Services

May:

- load registries and manifests
- resolve task packets
- mutate `docx` deterministically
- bind anchors
- validate structure and layout
- emit trace artifacts

May not:

- invent new requirements
- rewrite user intent
- silently weaken risk rules

## Call Contract Fields

Every routed call should resolve to these concepts:

- trigger
- caller
- target role
- allowed inputs
- allowed tools or services
- expected output schema
- approval mode
- failure behavior
- handoff destination

## Default Runtime Routing

### Task Understanding

- caller: orchestrator
- target: AI role
- output: task interpretation or plan object

### Rule Translation

- caller: orchestrator or constraint analyst
- target: AI role plus deterministic validator
- output: normalized rule draft, then validated rule object

### Patch Execution

- caller: patch and assembly engineer
- target: deterministic runtime service only
- output: mutation report

### Validation

- caller: orchestrator or review path
- target: deterministic validator plus review pack
- output: findings and gate result

## No Double-Authority Rule

Only one layer should own each final decision:

- task interpretation: orchestrator path
- final mutation: deterministic runtime
- final review gate: validation/review path
- final publish decision: orchestrator plus approval policy
