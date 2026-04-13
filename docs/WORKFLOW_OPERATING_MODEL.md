# Workflow Operating Model

## Purpose

This document defines how the platform executes work safely and repeatedly.

## Core Principle

The platform should operate like a small engineering system with:

- explicit source layers
- bounded execution paths
- replayable runs
- human review gates where needed
- precise validation claims
- programmatic document execution for `docx`

## Standard Workflow

1. classify the request by task family
2. choose the nearest harness
3. identify truth layers and protected references
4. convert intent into managed objects, patch proposals, or generation inputs
5. perform the programmatic transformation or audit
6. verify at the appropriate scope
7. publish or record trace only after verification

## Current `docx` MVP Workflow

1. import prompt, template, brief, rubric, variable sheet, and source files
2. interpret constraints and missing requirements
3. plan the run and classify approval mode
4. produce section text, asset-generation code, or review findings through AI
5. convert the task into managed objects and patch proposals
6. execute `docx` writes, style changes, numbering, and layout changes through
   deterministic program logic
7. apply those writes only inside a document-edit sandbox copy
8. run structural and visual audits
9. present patch or merge proposals in the human review surface
10. promote only approved and verified results

## Truth-Layer Rule

Do not jump directly from conversational feedback to document mutation.

Preferred promotion order:

1. capture intent
2. convert it into managed or auditable objects
3. run the correct programmatic transform
4. verify results
5. promote only verified state

## Validation Scope Rule

All completion claims should identify whether they are:

- structural
- semantic
- layout
- compliance
- mixed

## Archive Rule

Archived cases may inform examples, benchmarks, and recovery patterns, but they
must not silently become the active workflow authority.

## Sandbox Rule

Interactive editing must target sandbox copies, not imported references or
archived case-study artifacts.

## Contract Rule

Meaningful automation or mutation work should be routed through:

- artifact graph objects
- patch proposals
- task packets
- agent registries
- provider adapters
- runtime command surfaces
- versioned prompt packs

Do not jump directly from conversational intent to uncontrolled file mutation.

## Memory And Trace Rule

If a change affects governance, harnesses, release semantics, or replay
navigation, update the local trace and the relevant index documents.

## Development Retrospective Rule

When a meaningful engineering stage closes, record a concise OfficeX
development-stage retrospective in the local trace and, when useful, summarize
it in the development history review register.
