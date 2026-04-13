# Agent Runtime Benchmark Framework

## Purpose

This framework is for testing whether external agentic CLI systems are actually
better than the current platform in ways that matter.

Do not use vague judgments such as:

- better prompts
- smarter feel
- cleaner UX

Use explicit dimensions with evidence.

## Benchmark Targets

- current platform:
  - `/Users/nihao/Documents/Playground/document-ops-system`
- official references:
  - Codex CLI
  - Claude Code
- optional ecosystem references:
  - curated secondary repos in `references/agent_cli/secondary`

## Benchmark Levels

### Level 1: Structural Benchmark

Question:

- does the external system define a stronger runtime structure than ours

Check:

- project instruction hierarchy
- settings hierarchy
- memory model
- command model
- skills model
- subagent model
- sandbox / approval model
- session / resume model
- plugin / extension model

### Level 2: Operational Benchmark

Question:

- does the external system operate with fewer ambiguous transitions than ours

Check:

- when it asks for approval
- when it stops
- when it resumes
- when it delegates
- how it scopes tools
- how it separates user, project, and managed policy

### Level 3: Adaptation Benchmark

Question:

- which external ideas can be adopted safely into our platform

Check:

- low-risk borrow:
  - naming patterns
  - settings hierarchy
  - plugin structure
  - command structure
- medium-risk borrow:
  - memory layering
  - subagent triggering
  - approval policy
- high-risk borrow:
  - prompt contracts
  - execution assumptions
  - repo-bound coding behaviors that do not fit deliverable work

## Evaluation Dimensions

### D1 Instruction Hierarchy

Measure:

- does the system clearly separate global, project, local, and managed rules

Why it matters:

- our current memory and governance system needs better scoped precedence

### D2 Memory Layering

Measure:

- does the system separate:
  - stable policy
  - project memory
  - user preference
  - transient session state
  - archived historical memory

Why it matters:

- this is one of the most important areas for redesign

### D3 Specialist Agent Model

Measure:

- does the system define:
  - clear subagent scope
  - trigger conditions
  - ownership boundaries
  - output contracts

Why it matters:

- our current harness system is stronger on playbooks than on typed agent roles

### D4 Command and UX Surface

Measure:

- does the system provide reusable commands for recurring workflows

Why it matters:

- this affects app, web, extension, and CLI convergence

### D5 Approval and Safety Model

Measure:

- what can auto-run
- what requires confirmation
- what is forbidden
- whether managed policy can override local flexibility

Why it matters:

- this is essential once the product evolves beyond CLI into app/web/extension

### D6 Resume and Replay

Measure:

- named sessions
- resume flow
- replay state
- explicit interruption handling

Why it matters:

- our trace system is strong, but it needs to evolve into a true runtime model

### D7 Plugin / Skill / Hook Extensibility

Measure:

- can external capability be added without corrupting the core runtime

Why it matters:

- we need a durable extension story for domain deliverables

### D8 Deliverable Fitness

Measure:

- does the borrowed mechanism work for formal deliverables rather than only for
  code repos

Why it matters:

- coding-agent patterns are useful, but not all transfer cleanly

## Scoring Template

Use this scale:

- `0`: absent
- `1`: present but weak
- `2`: usable
- `3`: strong
- `4`: production-grade and worth borrowing

For each benchmark target, record:

- score
- evidence path or URL
- adopt / adapt / reject decision
- migration risk

## Immediate Comparison Set

### Compare against Codex for

- `AGENTS.md` hierarchy
- skills
- config layering
- sandbox/approval concepts

### Compare against Claude Code for

- memory and settings hierarchy
- plugins / hooks / commands / agents split
- strict policy examples
- agent-creation prompt patterns

## Output Requirement

When we run comparisons later, every finding should be recorded as:

- benchmark dimension
- source
- evidence
- relevance to our runtime
- adoption recommendation
