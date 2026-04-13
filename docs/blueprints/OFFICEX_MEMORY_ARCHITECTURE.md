---
doc_id: officex_memory_architecture
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Memory Architecture

## Core Position

Use `RAG`, but do not make `RAG` the sole memory system.

The stricter active policy for this area lives in:

- [MEMORY_LAYERING_AND_RAG_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md)

The platform should use layered memory:

1. constitutional and policy memory
2. structured index memory
3. trace and checkpoint memory
4. issue and lessons memory
5. prompt-history memory
6. retrieval-augmented memory

## Memory Layers

### Layer 1: Hard Governance

Files such as:

- `AGENTS.md`
- `PROJECT.md`
- architecture and workflow docs

These are not inferred from embeddings. They are explicit authority.

### Layer 2: Structured Indexes

Files such as:

- `navigation_catalog.yml`
- `memory_index_policy.yml`
- `harness_catalog.yml`
- `reference_catalog.yml`

These are the machine-readable routing layer.

### Layer 3: Trace

Files such as:

- `CURRENT_STATE.md`
- `REPLAY.md`
- `CHECKPOINT_*.md`

These preserve replayable evolution and active-state recovery.

### Layer 4: Registers

Files such as:

- engineering issues
- historical case issues
- scaffold lessons

These preserve failures, blockers, and repeated lessons.

### Layer 5: Prompt History

Important user prompts should be archived and indexed so later runs can recover
design intent that is not obvious from code alone.

### Layer 6: RAG

`RAG` should sit on top of the prior layers.

Use it for:

- retrieving relevant historical prompts
- retrieving past issues and lessons
- retrieving reference snippets from official corpora
- retrieving archived case context without loading entire histories

Do not use it to override:

- hard governance
- current active state
- explicit product decisions

## Retrieval Precedence

Preferred order:

1. active governance
2. active blueprint docs
3. active trace
4. machine-readable indexes
5. issue and lessons registers
6. prompt history
7. archived cases
8. RAG retrieval over the above corpora

## RAG Corpus Design

Recommended corpus partitions:

- active platform docs
- active trace
- issue registers
- prompt history
- official reference corpus
- archived case studies

Do not mix all chunks into one undifferentiated vector space.

## Promotion Rule

If RAG repeatedly surfaces useful material, promote it into:

- a register
- a blueprint
- a manifest
- or a checkpoint

RAG is retrieval support, not the final home of durable decisions.
