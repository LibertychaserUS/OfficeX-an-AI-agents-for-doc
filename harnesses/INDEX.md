# Harness Index

## Purpose

Harnesses are reusable execution playbooks for recurring document-engineering
task families.

## Active Harnesses

- [document_ingestion.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/document_ingestion.md)
- [document_generation.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/document_generation.md)
- [document_revision.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/document_revision.md)
- [template_alignment.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/template_alignment.md)
- [asset_binding.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/asset_binding.md)
- [compliance_review.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/compliance_review.md)
- [render_audit.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/render_audit.md)
- [publication_release.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/publication_release.md)

## Selection Heuristic

- use `document_ingestion` when the starting point is an external document or artifact
- use `document_generation` when the starting point is managed source material
- use `document_revision` when the starting point is review feedback on an existing candidate
- use `template_alignment` when layout/template drift is the main risk
- use `asset_binding` when evidence identity or snippet mapping is the main risk
- use `compliance_review` when the main question is conformance, not transformation
- use `render_audit` when readability or page composition is the main risk
- use `publication_release` when canonical promotion, summaries, or release notes are involved
