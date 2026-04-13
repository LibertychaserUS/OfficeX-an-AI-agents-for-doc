# Memory And Harness Evolution Note

## Purpose

This note records cautious, reference-driven improvements for the platform's
memory and harness system.

It is not a command to rewrite the active runtime immediately.

## Current State

The platform already has:

- trace and checkpoints
- replay bootstrap
- navigation catalog
- harness catalog
- memory index policy

This is stronger than a typical tool, but it is still closer to a
document-engineering workbench than to a mature agent runtime.

## Key Reference Lessons

### From Codex

- `AGENTS.md` is treated as a real operational contract, not marketing copy
- skills are separate from core instructions
- config and sandbox policy are first-class
- command surfaces are explicit

### From Claude Code

- settings hierarchy is clear
- managed policy and strict-mode examples are explicit
- plugins separate:
  - commands
  - agents
  - skills
  - hooks
- prompt-design references are structured and operational

### From broader agent-runtime references

- sessions should be durable
- handoffs should be typed
- guardrails should be explicit
- workflow control should not be fully delegated to free-form LLM behavior

## Cautious Redesign Direction

### 1. Split memory into layers

Current memory artifacts should evolve into:

- `managed_policy`
  - enterprise or deployment-enforced rules
- `platform_governance`
  - current product-level operating rules
- `workspace_memory`
  - project or deliverable-pack memory
- `user_preference_memory`
  - user-local preferences
- `run_state`
  - ephemeral session state
- `archive_memory`
  - read-only historical case-study memory

This is better than relying on one mixed memory index plus trace summaries.

### 2. Separate harnesses from commands and agents

Current harnesses are reusable playbooks. Keep that.

But add two new categories conceptually:

- `agents`
  - specialist execution roles with trigger conditions and output contracts
- `commands`
  - named workflow entrypoints for app/web/extension/CLI surfaces

Recommended relationship:

- commands call orchestrator entrypoints
- orchestrator selects agents
- agents execute with tool constraints
- harnesses provide structured playbooks and acceptance criteria

### 3. Add an approval-policy layer

Current platform docs mention caution, but approval is not yet modeled as a
strong runtime object.

We should eventually define:

- auto-allow
- ask
- deny
- managed-only

This should apply to:

- tool classes
- publication
- destructive edits
- evidence-sensitive operations
- external fetch

### 4. Introduce named sessions and session memory

Trace is good for recovery.

But the next step is a session model that explicitly tracks:

- session id
- workspace id
- active goal
- selected profile
- pending approvals
- unresolved questions
- recent agent handoffs

### 5. Distinguish active memory from archived memory

Archived product traces and case studies must never silently act like active
runtime memory.

This boundary already exists conceptually and should become stricter in future
runtime design.

## Suggested Future Files

Do not create all of these immediately. They are a target model.

- `manifests/managed_policy.yml`
- `manifests/approval_policy.yml`
- `manifests/agent_registry.yml`
- `manifests/command_registry.yml`
- `manifests/session_policy.yml`
- `memory/workspaces/...`
- `memory/users/...`
- `memory/archive/...`

## Low-Risk Near-Term Improvements

- add a machine-readable reference catalog
- add benchmark docs
- add explicit reference area to navigation
- start distinguishing:
  - active platform memory
  - research references
  - archived case-study memory

## Medium-Risk Future Improvements

- introduce command registry
- introduce agent registry
- add managed policy layer
- upgrade replay into session-oriented recovery

## High-Risk Changes To Delay

- immediate package rename
- full trace model replacement
- replacing harnesses before command/agent separation is designed clearly
- copying code-agent prompt structures directly into deliverable runtime

## Decision Rule

Borrow patterns, not assumptions.

If a Codex or Claude mechanism is repo-centric, code-centric, or tool-centric
in a way that does not fit formal deliverables, adapt it rather than copying it.
