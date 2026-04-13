---
doc_id: officex_materials_and_citation_graph
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Materials And Citation Graph

## Purpose

OfficeX should not treat the materials library as a loose text corpus.

The active model is an object graph, with retrieval only as an assistive layer.

## Core Objects

### Source Document

Represents a source artifact such as:

- paper
- web page
- internal memo
- policy document
- code file
- interview record

Required concepts:

- source id
- origin
- source type
- version
- retrieval path
- trust level

### Source Fragment

Represents an extracted usable fragment from a source document.

Required concepts:

- fragment id
- parent source id
- location selector
- fragment text or structured content
- extraction method
- verification state

### Claim

Represents a statement intended for document use.

Required concepts:

- claim id
- claim type
- claim text
- linked source fragments
- verification state
- allowed usage contexts

### Citation

Represents a rendered reference form.

Required concepts:

- citation id
- source document id
- citation profile
- rendered reference text
- provenance link

### Usage Context

Represents where a claim, citation, or source fragment is used.

Examples:

- section
- paragraph
- appendix
- figure note
- table note

## Verification States

The graph should support at least:

- verified
- source_linked
- user_confirmed
- unresolved
- prohibited

## Hard Rules

- no source fragment, no factual claim
- no mapped source document, no citation emission
- no usage context, no silent insertion into the document
- no version boundary, no stable replay claim

## Retrieval Rule

RAG or vector retrieval may assist with:

- finding relevant source fragments
- surfacing likely supporting materials
- identifying similar prior usage

It may not become the authority for:

- claim truth
- citation truth
- approval state
- final source-to-claim binding
