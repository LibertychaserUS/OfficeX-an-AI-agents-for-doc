# REPLAY

## Fast Resume

1. read [PROJECT.md](/Users/nihao/Documents/Playground/document-ops-system/PROJECT.md)
2. read [AGENTS.md](/Users/nihao/Documents/Playground/document-ops-system/AGENTS.md)
3. read [docs/ACTIVE_RULES_AND_PATHS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md)
4. read [docs/CONSTRAINT_INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/CONSTRAINT_INDEX.md)
5. read [docs/PRODUCT_ROADMAP.md](/Users/nihao/Documents/Playground/document-ops-system/docs/PRODUCT_ROADMAP.md)
6. read [docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md)
7. read [docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md)
8. read [docs/REVIEW_ANCHOR_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/REVIEW_ANCHOR_PROTOCOL.md)
9. read [docs/VISUAL_AUDIT_REQUIREMENTS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/VISUAL_AUDIT_REQUIREMENTS.md)
10. read [docs/OPEN_SOURCE_EDITOR_EVALUATION.md](/Users/nihao/Documents/Playground/document-ops-system/docs/OPEN_SOURCE_EDITOR_EVALUATION.md)
11. read [docs/ENGINEERING_ISSUES_REGISTER.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ENGINEERING_ISSUES_REGISTER.md)
12. read [manifests/provider_catalog.yml](/Users/nihao/Documents/Playground/document-ops-system/manifests/provider_catalog.yml)
13. read [manifests/agent_catalog.yml](/Users/nihao/Documents/Playground/document-ops-system/manifests/agent_catalog.yml)
14. read [prompts/OFFICEX_COGNITION.md](/Users/nihao/Documents/Playground/document-ops-system/prompts/OFFICEX_COGNITION.md)
15. read [docs/research/DOCX_RUNTIME_REFERENCE_INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/research/DOCX_RUNTIME_REFERENCE_INDEX.md)
16. read the latest local checkpoint in [CHECKPOINT_16.md](/Users/nihao/Documents/Playground/document-ops-system/trace/CHECKPOINT_16.md)
17. confirm current platform state in [CURRENT_STATE.md](/Users/nihao/Documents/Playground/document-ops-system/trace/CURRENT_STATE.md)
18. inspect the local checkpoint catalog in [checkpoint_catalog.md](/Users/nihao/Documents/Playground/document-ops-system/trace/checkpoint_catalog.md)
19. read [harnesses/INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/INDEX.md) only after runtime governance and current state are clear

## Smoke Commands

```bash
.venv/bin/python -m tools.report_scaffold_v3.cli check-package
.venv/bin/python -m tools.report_scaffold_v3.cli officex prompt show --role orchestrator --role-only
.venv/bin/python -m tools.report_scaffold_v3.cli officex provider list
.venv/bin/python -m tools.report_scaffold_v3.cli officex provider build-request --provider openai --role orchestrator --run-id replay-smoke --sandbox-root /tmp/officex-replay-smoke --config-field api_key=demo --config-field model_id=gpt-5.4 --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex agent list
.venv/bin/python -m tools.report_scaffold_v3.cli officex workspace init --workspace-id replay-smoke --workspace-root /tmp/officex-replay-workspaces --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task run-docx-mvp --run-id replay-smoke --sandbox-root /tmp/officex-replay-smoke
.venv/bin/python -m tools.report_scaffold_v3.cli officex task inspect --run-id replay-smoke --sandbox-root /tmp/officex-replay-smoke --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task build-review-ledger --review-findings /tmp/officex-review-input.json --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task extract-anchors --candidate-docx /tmp/officex-replay-smoke/replay-smoke/candidate/minimal_writer_demo.docx --review-ledger /tmp/officex-review-ledger.json --as-json
.venv/bin/python -m tools.report_scaffold_v3.cli officex task apply-patch-bundle --patch-bundle /tmp/officex-patch-bundle.json --candidate-docx /tmp/officex-replay-smoke/replay-smoke/candidate/officex_docx_mvp_template.docx --anchor-snapshot /tmp/officex-live-anchor-snapshot.json --dry-run --as-json
.venv/bin/pytest -q
.venv/bin/python -m tools.report_scaffold_v3.cli index-trace
```
