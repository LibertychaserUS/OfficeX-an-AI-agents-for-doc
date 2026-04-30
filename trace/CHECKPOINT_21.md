# CHECKPOINT_21

date: 2026-04-20

## Title

Prompt compiler structure and CLI clarification

## Summary

- Provider prompt assembly now emits prompt manifest, resolved refs, compiled prompt debug, and prompt trace metadata instead of only opaque string concatenation.
- Human-readable provider outputs now summarize prompt layers and resolved refs while keeping compiled prompt available as a debug artifact.

## Verification

- pytest -q -> 154 passed.
- check-package -> pass.
- officex task run-docx-mvp --run-id prompt-compiler-smoke --sandbox-root /tmp/officex-prompt-compiler-smoke --as-json -> pass.
- officex provider build-request --provider openai --role orchestrator --run-id prompt-compiler-smoke --sandbox-root /tmp/officex-prompt-compiler-smoke --config-field api_key=demo --config-field model_id=gpt-5.4 --response-contract-kind plan_object --as-json -> pass.

## Follow-up

- Next step is to promote prompt manifest refs from simple markdown-layer imports into narrower section-level rule imports and provider-targeted compile passes.
