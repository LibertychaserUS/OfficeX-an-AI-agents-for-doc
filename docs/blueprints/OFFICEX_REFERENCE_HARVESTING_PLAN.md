---
doc_id: officex_reference_harvesting_plan
layer: blueprint
authority: active
status: living
owner: document_intelligence_engineering
machine_source_of_truth: false
---

# OfficeX Reference Harvesting Plan

## Purpose

Many academic, technical, and publisher pages already expose structured or
semi-structured citation formats.

OfficeX should prefer harvesting and normalizing those references over asking
models to invent citation strings.

## First-Stage Inputs

- paper landing pages
- publisher pages
- standards pages
- documentation pages
- internal reference pages with stable metadata

## First-Stage Outputs

- normalized source document record
- rendered citation candidate
- provenance metadata
- harvesting confidence

## Harvesting Order

1. page-native citation block
2. explicit metadata tags
3. stable bibliographic fields in page content
4. manual review fallback

## Hard Rule

Harvested references may become citation candidates.

They do not become final accepted references until they are normalized into the
materials and citation graph.
