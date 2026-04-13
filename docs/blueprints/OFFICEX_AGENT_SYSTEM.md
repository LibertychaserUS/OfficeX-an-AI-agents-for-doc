---
doc_id: officex_agent_system
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Agent System

## Purpose

This document defines the recommended agent system for the `docx` MVP.

It answers four questions:

- how many agent types should exist now
- how many instances should run per task
- what each agent owns
- how multi-agent document work stays low-coupling and auditable

## Design Position

`OfficeX` should behave like a document-task runtime, not like a generic chat
assistant and not like an editor plugin with one oversized prompt.

The system should feel closer to a publisher team plus review desk:

- one lead editor
- several section writers
- a visual and asset desk
- a production desk
- an audit and standards desk

## MVP Recommendation

### Agent Type Count

For the `docx` MVP, support `6` core agent types.

This is enough to create a full generation-review-assembly loop without making
handoffs, prompts, and debugging unnecessarily complex.

### Runtime Instance Count

For one normal task, run `4` to `8` active instances.

Do not exceed `10` active instances in the first MVP unless the task is
explicitly benchmarked for larger fan-out.

The system should scale by replicating worker instances, not by inventing many
more agent types.

## Core Agent Types

### 1. OfficeX Orchestrator

Owns:

- task understanding
- workflow selection
- approval mode selection
- shared context pack
- task decomposition
- final merge decisions
- final publish gate

May do:

- ask for missing high-risk inputs
- route work to worker agents
- approve or reject patch bundles
- stop the run when drift appears

May not do alone:

- silently redefine platform rules
- bypass validation gates
- publish unreviewed high-risk changes

### 2. Constraint Analyst

Owns:

- template parsing
- rubric parsing
- brief parsing
- review-result parsing
- requirement extraction
- hard-vs-soft rule classification

Outputs:

- normalized constraint set
- missing requirement list
- escalation notes for ambiguous rules

May not do:

- final text writing
- final layout mutation
- silent rule invention

### 3. Writer

Owns:

- section drafting
- section rewriting
- tone adjustment
- bounded content improvement

Scaling rule:

- replicate this type for multi-section jobs
- each writer instance should own one section block or one bounded chapter set

May do:

- generate section text
- propose inline content edits
- request missing evidence

May not do:

- mutate shared numbering
- change page setup
- change document-wide style authority
- invent citations or unsupported facts

### 4. Asset Engineer

Owns:

- charts
- tables
- diagrams
- generated images
- caption drafts
- asset-generation code

May do:

- write deterministic generation code
- propose insertion anchors
- produce asset metadata

May not do:

- freehand visual placement as final authority
- change unrelated body text
- bypass layout validation

### 5. Patch And Assembly Engineer

Owns:

- patch bundle preparation
- deterministic `docx` execution inputs
- numbering updates
- style application inputs
- bounded merge of approved worker outputs

This role is the production desk.

It converts AI outputs into:

- content patches
- style patches
- layout patches
- asset patches
- metadata patches

May not do:

- redefine constraints
- override approvals
- publish without validation

### 6. Validation And Review Auditor

Owns:

- structure audit
- rubric audit
- truthfulness audit
- professionalism audit
- feasibility audit
- layout audit
- visual risk escalation
- release-readiness judgement

Outputs:

- issue list
- severity
- pass / partial / fail outcomes
- required rework scope

May not do:

- silently patch the document as part of auditing
- downgrade high-risk issues without evidence

## Review Specialization Packs

The MVP should keep one review-oriented agent type, but that type must support
multiple specialization packs and multiple concurrent reviewer instances.

This preserves low coupling while allowing deeper content review.

### Core Review Packs

- `general_quality_review`
  - checks clarity, structure, redundancy, and weak phrasing
- `truth_and_fact_review`
  - checks factual claims, source linkage, and unsupported statements
- `feasibility_review`
  - checks whether plans, claims, or recommendations are operationally plausible
- `professional_language_review`
  - checks whether wording matches the expected professional register
- `authority_reference_review`
  - checks whether cited rules, standards, laws, cases, or sources are real and relevant

### Domain-Specific Packs

These should be loaded only when the selected profile requires them.

- `legal_wording_review`
  - checks legal wording, legal caution, and whether references are real and on point
- `academic_reference_review`
  - checks citation discipline, claim support, and source fit
- `business_feasibility_review`
  - checks whether business recommendations and plans are commercially coherent
- `compliance_language_review`
  - checks whether wording and stated controls align with the imported compliance standard

### High-Risk Domain Rule

For legal, finance, regulated compliance, or other high-risk profiles:

- review packs should activate before publish
- autonomous content generation should remain more conservative
- unsupported authority claims must be refused or clearly marked unresolved

These packs should first be implemented as review and challenge layers, not as
silent replacement for licensed professional judgement.

## Shared Context Pack

Every worker instance must inherit the same bounded context pack.

It should include:

- workspace id
- run id
- deliverable type
- document title
- audience
- selected profile
- approval mode
- page profile
- variable set
- truthfulness rules
- applicable constraints
- glossary and naming conventions
- forbidden assumptions

Workers should not rebuild these assumptions independently.

## Ownership Rules

### Hard Ownership

Each mutable object should have one current owner.

Examples:

- one writer owns section `2.1` to `2.3`
- one asset engineer owns figure set `F1-F3`
- one assembly engineer owns numbering and merge state

### Shared Objects

The following are shared and should only be changed by the orchestrator or the
assembly role:

- document-wide numbering
- page profile
- style authority
- output path
- publish metadata

### Cross-Scope Change Rule

If a worker needs a change outside its owned scope, it should emit a request,
not apply the change directly.

## Handoff Contract

Every agent handoff should be typed and bounded.

Minimum handoff fields:

- `task_id`
- `workspace_id`
- `run_id`
- `agent_type`
- `assigned_scope`
- `forbidden_scope`
- `input_artifacts`
- `constraint_subset`
- `required_outputs`
- `approval_mode`
- `escalation_conditions`

Natural-language instructions may exist, but they should not be the only
contract.

## Default Collaboration Shape

For a normal report-like task, use:

- `1` orchestrator
- `1` constraint analyst
- `2` to `4` writer instances
- `1` asset engineer
- `1` patch and assembly engineer
- `1` validation and review auditor

This creates a practical runtime range of `6` to `8` instances.

For higher-risk or more formal tasks, add one or two extra reviewer instances
under the same review agent type, for example:

- one `truth_and_fact_review` instance
- one `professional_language_review` or `legal_wording_review` instance

## Approval Interaction

The agent system must respect the active approval mode:

- `review_only`
- `ask_every_conflict`
- `scoped_auto_low_medium`
- `full_auto_in_sandbox`

High-risk conflicts should still stop for review or refusal, even in more
autonomous modes.

## Why Not More Agent Types Yet

The first bottlenecks are:

- anchor stability
- patch quality
- merge quality
- validation quality

They are not solved by adding many role labels.

The correct MVP strategy is:

- few types
- hard boundaries
- replicable worker instances
- strong assembly and audit

## Candidate Future Specializations

Add only after the core six roles are stable:

- truth auditor
- visual audit specialist
- review-to-rule compiler
- citation normalizer
- section integrator
- memory curator

These should be added only when they reduce ambiguity and benchmark better than
the six-role baseline.

## Engineering Guidance

When implementing the OfficeX agent runtime:

1. keep agent types stable
2. scale through worker replication first
3. keep contracts typed
4. keep merge authority narrow
5. keep audits independent from writing
6. keep archive knowledge out of active runtime assumptions
