# CHECKPOINT_05

date: 2026-04-12

## Title

Official `docx` runtime reference corpus established

## Summary

- A separated local reference corpus was created for `docx` runtime and
  collaborative editor comparison.
- Official repositories were cloned into:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/onlyoffice-documentserver`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/collabora-online`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/open-xml-sdk`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/python-docx`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/document_runtime/official/overleaf`
- A dedicated local reference index was added at:
  - `/Users/nihao/Documents/Playground/document-ops-system/docs/research/DOCX_RUNTIME_REFERENCE_INDEX.md`
- Navigation and manifest indexes were updated so these references can be used
  without mixing them into active platform code.

## Boundary

- These repositories are reference-only.
- They do not redefine active governance.
- They remain separated from both active platform code and archived LoopMart
  product code.

## Follow-up

- compare editor-surface and OOXML execution patterns against the current MVP
- derive concrete implementation steps without copying external architecture
  blindly
