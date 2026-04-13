---
doc_id: domain_agent_registry
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Domain Agent Registry

## Purpose

This document defines how OfficeX loads domain-specialized agent behavior
without exploding the number of hard-coded runtime agent types.

The registry should separate:

- core runtime agent types
- domain packs
- review packs
- memory packs
- activation rules

## Core Runtime Agent Types

The `docx` MVP keeps the six-role runtime:

- orchestrator
- constraint analyst
- writer
- asset engineer
- patch and assembly engineer
- validation and review auditor

These are the stable operational roles.

## Domain Pack Principle

Domain specialization should be attached through packs, not by inventing a new
top-level runtime architecture for every field.

Each domain pack may add:

- terminology guidance
- output expectations
- truthfulness cautions
- review criteria
- reference expectations
- feasibility heuristics

## Candidate Domain Packs

### Academic

Use when the task targets reports, assessments, essays, dissertations, or
institutional submissions.

Primary concerns:

- rubric coverage
- source discipline
- citation consistency
- academic tone
- evidence-backed claims

### Legal

Use when the task targets legal memoranda, legal-style letters, contract
support drafts, case summaries, or legal review material.

Primary concerns:

- precise wording
- authority verification
- citation relevance
- risk-aware language
- explicit unresolved status where authority is missing

### Business

Use when the task targets proposals, plans, executive summaries, strategy
documents, or operational reports.

Primary concerns:

- commercial coherence
- feasibility
- concise professional language
- actionability
- internal consistency

### Compliance

Use when the task targets policy mappings, control narratives, review findings,
corrective-action plans, or standards-backed operational documents.

Primary concerns:

- control wording
- standard alignment
- requirement traceability
- evidentiary support
- clear pass/fail logic

### Finance

Use when the task includes financial summaries, budgets, variance explanations,
financial-control commentary, or metric-backed business outputs.

Primary concerns:

- arithmetic correctness
- conservative wording
- traceable figures
- disclosure discipline
- explicit uncertainty handling

### Technical

Use when the task targets architecture docs, engineering reports, technical
plans, specifications, or system analysis.

Primary concerns:

- accuracy of technical claims
- precise structure
- reproducibility
- terminology consistency
- implementation realism

### Proposal

Use when the task is persuasive and deliverable-driven.

Primary concerns:

- audience fit
- persuasive structure
- scope clarity
- feasibility
- aligned visuals and tables

### Project Plan

Use when the task emphasizes sequencing, milestones, dependencies, owners, or
execution risk.

Primary concerns:

- chronology
- deliverable feasibility
- dependency correctness
- role clarity
- measurable checkpoints

## Review Pack Mapping

Each domain pack should map to one or more review packs.

Examples:

- academic
  - `general_quality_review`
  - `truth_and_fact_review`
  - `academic_reference_review`
- legal
  - `professional_language_review`
  - `authority_reference_review`
  - `legal_wording_review`
- business
  - `general_quality_review`
  - `business_feasibility_review`
- compliance
  - `authority_reference_review`
  - `compliance_language_review`
- finance
  - `truth_and_fact_review`
  - `feasibility_review`
  - financial review pack to be added after benchmark support

## Activation Rules

### Automatic Activation

Auto-activate a domain pack only when at least one of the following is true:

- the task family strongly implies the domain
- imported rubric or brief explicitly names the domain
- template metadata declares the domain
- user explicitly requests it

### Confirmation Rule

If multiple domains seem plausible and the choice changes review severity or
writing style materially, ask for confirmation unless the current approval mode
allows low-risk auto-selection.

### High-Risk Rule

Legal, finance, and regulated compliance packs should be treated as high-risk
profiles:

- stronger review packs
- more conservative writing
- stricter authority checks
- fewer silent assumptions

## Memory Attachment

Every domain pack may attach:

- domain glossary
- domain reviewer heuristics
- domain prompt supplements
- approved reference priorities

These attachments must be versioned and may not override system hard policy.

## Promotion Rule

New domain packs should not become active by prompt habit alone.

Promotion sequence:

1. draft the pack
2. benchmark it
3. review failure modes
4. approve it
5. register it

## MVP Rule

The first implementation does not need every domain pack fully wired.

It does need:

- registry structure
- activation rules
- clear distinction between core roles and domain behavior
