---
doc_id: docx_runtime_reference_index
layer: research
authority: active_reference
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Docx Runtime Reference Index

## Purpose

This index tracks official external repositories used to benchmark `OfficeX`
against existing document-editing, OOXML, and collaborative document systems.

These repositories are reference-only. They must not be mixed into active
platform code or treated as implicit product requirements.

## Local Reference Root

- `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official`

## Official Repositories

### ONLYOFFICE Docs Community Edition

- local path:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/onlyoffice-documentserver`
- why it matters:
  - Office-like collaborative editing surface
  - `docx`-oriented editor experience
  - useful embedded-editor reference for the MVP mirror surface
- key entrypoints:
  - [README.md](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/onlyoffice-documentserver/README.md)
  - [LICENSE.txt](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/onlyoffice-documentserver/LICENSE.txt)
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/onlyoffice-documentserver/sdkjs`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/onlyoffice-documentserver/web-apps`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/onlyoffice-documentserver/server`
- current OfficeX takeaway:
  - good primary candidate for an embedded Office-style mirror surface
  - Community Edition should be treated conservatively around advanced
    external-connector assumptions
  - prefer editor lifecycle, open/save, and controlled reload patterns for MVP

### Collabora Online

- local path:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/collabora-online`
- why it matters:
  - open-source embedded office surface
  - integration model, browser client, and WOPI-style collaboration reference
  - strong comparison point for self-hosted editor architecture
- key entrypoints:
  - [README.md](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/collabora-online/README.md)
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/collabora-online/browser`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/collabora-online/wsd`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/collabora-online/test`
- current OfficeX takeaway:
  - strong long-term comparison point for open integration patterns
  - WOPI and postMessage architecture are useful reference material
  - heavier protocol surface makes it a comparison target rather than first MVP embed

### Microsoft Open XML SDK

- local path:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/open-xml-sdk`
- why it matters:
  - authoritative OOXML object and package manipulation reference
  - diagnostics and sample patterns for deterministic `docx` execution
- key entrypoints:
  - [README.md](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/open-xml-sdk/README.md)
  - [Features.md](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/open-xml-sdk/docs/Features.md)
  - [Diagnostics.md](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/open-xml-sdk/docs/Diagnostics.md)
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/open-xml-sdk/samples`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/open-xml-sdk/src`

### python-docx

- local path:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/python-docx`
- why it matters:
  - Python-side `docx` reading and writing reference
  - useful for current-language prototyping and fixture understanding
- key entrypoints:
  - [README.md](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/python-docx/README.md)
  - [docs/index.rst](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/python-docx/docs/index.rst)
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/python-docx/src`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/python-docx/tests`

### Overleaf Community Edition

- local path:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/overleaf`
- why it matters:
  - collaboration workspace and project-surface reference
  - versioning, commenting, and multi-user document workflow ideas
  - not a `docx` engine reference
- key entrypoints:
  - [README.md](/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/overleaf/README.md)
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/overleaf/doc`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/overleaf/server-ce`

## Recommended Use

- use `Open XML SDK` and `python-docx` to reason about deterministic OOXML
  mutation
- use `ONLYOFFICE` and `Collabora` to reason about embedded editing surfaces
  and integration models
- use `Overleaf` to reason about collaborative document workspace design

## Boundary

- do not copy external logic without comparing it to the current platform model
- do not let reference repositories silently redefine active governance
- keep editor references separate from agent-runtime references
