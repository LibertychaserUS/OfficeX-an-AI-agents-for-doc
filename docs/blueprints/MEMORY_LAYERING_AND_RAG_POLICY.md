---
doc_id: memory_layering_and_rag_policy
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Memory Layering And RAG Policy

## Purpose

This document defines the strict memory hierarchy for OfficeX.

Its main goal is to prevent retrieval systems from becoming accidental sources
of governance truth.

## Core Rule

RAG is retrieval support.

RAG is not:

- governance authority
- prompt authority
- harness authority
- release authority
- active-state authority

## Memory Layers

### Layer 1. Authoritative System Memory

Contains:

- constitutions
- policies
- approved prompt packs
- active registries
- harness catalog
- agent registry
- release rules

Requirements:

- file-backed
- versioned
- reviewable
- rollbackable

### Layer 2. Operational Memory

Contains:

- current workspace state
- run state
- approvals
- patch logs
- issue logs
- checkpoints
- trace state

Requirements:

- structured
- appendable
- current-session aware
- explicitly scoped

### Layer 3. User And Project Memory

Contains:

- tone preferences
- profile preferences
- common variable defaults
- recurring workflow habits
- project vocabulary

Requirements:

- scoped by user or project
- never stronger than system hard rules
- promotable only with explicit review if generalized

### Layer 4. Retrieval Memory

Contains:

- archived cases
- official references
- community references
- historical prompts
- candidate heuristics

Requirements:

- retrieval-oriented
- citation-aware
- never directly authoritative

## Precedence Order

When conflicts exist, use this order:

1. authoritative system memory
2. operational memory
3. active user/project memory
4. archived references
5. RAG results over approved corpora

## RAG Usage Policy

RAG may be used to:

- find relevant archived issues
- find similar prior prompts
- find reference snippets
- find candidate domain guidance
- find supporting examples

RAG may not be used to:

- redefine prompt packs
- redefine approval semantics
- redefine truthfulness policy
- redefine harness behavior
- redefine publish rules

## Promotion Rule

If retrieval keeps surfacing the same useful pattern, promote it explicitly into
one of:

- a registry
- a blueprint
- a policy
- an approved prompt pack
- an issue register

Do not leave durable knowledge trapped in embeddings.

## Partition Rule

RAG corpora should remain partitioned.

Minimum partitions:

- active platform docs
- active trace
- issue registers
- prompt history
- official references
- archived cases
- community references

## Audit Rule

When retrieval materially influences a decision, the run should be able to say:

- what corpus was queried
- what document was retrieved
- whether the result was advisory or authoritative
