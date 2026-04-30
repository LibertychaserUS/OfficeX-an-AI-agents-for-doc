# Constraint Index

## Purpose

This file routes platform governance to the correct long-lived document.

The platform distinguishes:

- constraints
- blueprints
- workflow rules
- architecture decisions
- harness playbooks
- review and audit protocols
- issue registers
- roadmap and archive records

## Priority Order

1. [AGENTS.md](/Users/nihao/Documents/Playground/document-ops-system/AGENTS.md)
2. product charter in [PROJECT.md](/Users/nihao/Documents/Playground/document-ops-system/PROJECT.md)
3. [ACTIVE_RULES_AND_PATHS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md)
4. architecture and workflow docs under [docs](/Users/nihao/Documents/Playground/document-ops-system/docs)
5. ADRs under [docs/adr](/Users/nihao/Documents/Playground/document-ops-system/docs/adr)
6. task-family harnesses under [harnesses](/Users/nihao/Documents/Playground/document-ops-system/harnesses)

## Routing Table

### Hard Boundary Or Safety Rule

Write to:

- [AGENTS.md](/Users/nihao/Documents/Playground/document-ops-system/AGENTS.md)
- [BOUNDARY.md](/Users/nihao/Documents/Playground/document-ops-system/BOUNDARY.md)

### Workflow Shape Or Promotion Rule

Write to:

- [WORKFLOW_OPERATING_MODEL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/WORKFLOW_OPERATING_MODEL.md)

### Architecture Or Layer Boundary

Write to:

- [ARCHITECTURE.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ARCHITECTURE.md)
- [docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCX_MVP_BLUEPRINT.md)
- [docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md)
- [docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md)
- [docs/blueprints/OFFICEX_AGENT_SYSTEM.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_AGENT_SYSTEM.md)
- [docs/blueprints/DOMAIN_AGENT_REGISTRY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DOMAIN_AGENT_REGISTRY.md)
- [docs/blueprints/PROMPT_EVOLUTION_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROMPT_EVOLUTION_PROTOCOL.md)
- [docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md)
- [docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md)
- [docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md)
- [docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md)
- [docs/blueprints/DEVELOPMENT_RETROSPECTIVE_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DEVELOPMENT_RETROSPECTIVE_PROTOCOL.md)
- [docs/blueprints/ARTIFACT_GRAPH_SCHEMA.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/ARTIFACT_GRAPH_SCHEMA.md)
- [docs/blueprints/PATCH_PROPOSAL_SCHEMA.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PATCH_PROPOSAL_SCHEMA.md)
- [docs/blueprints/AUTOMATION_TASK_PACKET_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/AUTOMATION_TASK_PACKET_CONTRACT.md)

### Multi-Agent Coordination Rule

Write to:

- [docs/blueprints/OFFICEX_AGENT_SYSTEM.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_AGENT_SYSTEM.md)
- [docs/blueprints/DOMAIN_AGENT_REGISTRY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DOMAIN_AGENT_REGISTRY.md)
- [MULTI_AGENT_WORKFLOW.md](/Users/nihao/Documents/Playground/document-ops-system/docs/MULTI_AGENT_WORKFLOW.md)
- [MULTI_AGENT_PROMPTS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/MULTI_AGENT_PROMPTS.md)

### Agent Registry Or Runtime Agent Mapping Rule

Write to:

- [docs/blueprints/OFFICEX_AGENT_SYSTEM.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_AGENT_SYSTEM.md)
- [docs/blueprints/DOMAIN_AGENT_REGISTRY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DOMAIN_AGENT_REGISTRY.md)
- [manifests/agent_catalog.yml](/Users/nihao/Documents/Playground/document-ops-system/manifests/agent_catalog.yml)

### Prompt Governance Or Pack Promotion Rule

Write to:

- [docs/blueprints/PROMPT_EVOLUTION_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROMPT_EVOLUTION_PROTOCOL.md)

### Memory Layering Or RAG Boundary Rule

Write to:

- [docs/blueprints/OFFICEX_MEMORY_ARCHITECTURE.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_MEMORY_ARCHITECTURE.md)
- [docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/MEMORY_LAYERING_AND_RAG_POLICY.md)

### Provider Integration Or Model Adapter Rule

Write to:

- [docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/PROVIDER_ADAPTER_CONTRACT.md)

### Desktop Shell Or Sidecar Runtime Rule

Write to:

- [docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md)
- [docs/blueprints/OFFICEX_MACOS_APP_DISTRIBUTION_BOUNDARY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_MACOS_APP_DISTRIBUTION_BOUNDARY.md)

### Development Execution Plan Or Milestone Archive

Write to:

- [docs/development/INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/development/INDEX.md)

### Product Entry Or First-Launch Rule

Write to:

- [docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md)
- [ACTIVE_RULES_AND_PATHS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md)
- [README.md](/Users/nihao/Documents/Playground/document-ops-system/README.md)

### Runtime CLI Surface Or Command Contract

Write to:

- [docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md)
- [ACTIVE_RULES_AND_PATHS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md)

### Release Baseline Or Backup Rule

Write to:

- [docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/RELEASE_BASELINE_AND_BACKUP_POLICY.md)

### Development-Stage Retrospective Rule

Write to:

- [docs/blueprints/DEVELOPMENT_RETROSPECTIVE_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/DEVELOPMENT_RETROSPECTIVE_PROTOCOL.md)
- [docs/registers/DEVELOPMENT_HISTORY_REVIEW_REGISTER.md](/Users/nihao/Documents/Playground/document-ops-system/docs/registers/DEVELOPMENT_HISTORY_REVIEW_REGISTER.md)

### Development Workflow Optimization Rule

Write to:

- [docs/development/INDEX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/development/INDEX.md)
- [docs/development/DEVELOPMENT_MEMORY_LAYERING.md](/Users/nihao/Documents/Playground/document-ops-system/docs/development/DEVELOPMENT_MEMORY_LAYERING.md)
- [docs/development/DEVELOPMENT_COMMAND_AGENT_KNOWLEDGEPACK_MODEL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/development/DEVELOPMENT_COMMAND_AGENT_KNOWLEDGEPACK_MODEL.md)
- [docs/development/DEVELOPMENT_TELEMETRY_AND_HOTSPOTS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/development/DEVELOPMENT_TELEMETRY_AND_HOTSPOTS.md)
- [docs/development/CROSS_MODEL_DEVELOPMENT_REVIEW.md](/Users/nihao/Documents/Playground/document-ops-system/docs/development/CROSS_MODEL_DEVELOPMENT_REVIEW.md)

### Recurring Execution Playbook

Write to:

- [harnesses](/Users/nihao/Documents/Playground/document-ops-system/harnesses)
- [harness_catalog.yml](/Users/nihao/Documents/Playground/document-ops-system/manifests/harness_catalog.yml)

### Roadmap, Incubation, Or Archived Case Placement

Write to:

- [PRODUCT_ROADMAP.md](/Users/nihao/Documents/Playground/document-ops-system/docs/PRODUCT_ROADMAP.md)

### Review Anchor Or Human Collaboration Rule

Write to:

- [REVIEW_ANCHOR_PROTOCOL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/REVIEW_ANCHOR_PROTOCOL.md)

### Visual Audit Or Page-Composition Rule

Write to:

- [VISUAL_AUDIT_REQUIREMENTS.md](/Users/nihao/Documents/Playground/document-ops-system/docs/VISUAL_AUDIT_REQUIREMENTS.md)
- [render_audit.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/render_audit.md)

### Open-Source Editor Or Integration Decision

Write to:

- [OPEN_SOURCE_EDITOR_EVALUATION.md](/Users/nihao/Documents/Playground/document-ops-system/docs/OPEN_SOURCE_EDITOR_EVALUATION.md)
- [docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_EDITOR_COMPATIBILITY_AND_CALLABILITY.md)

### Document Sandbox Or Mutable-Workspace Rule

Write to:

- [docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/OFFICEX_DOCUMENT_EDIT_SANDBOX.md)

### Automation Or Task-Packet Boundary

Write to:

- [docs/blueprints/AUTOMATION_TASK_PACKET_CONTRACT.md](/Users/nihao/Documents/Playground/document-ops-system/docs/blueprints/AUTOMATION_TASK_PACKET_CONTRACT.md)

### Living Issue Register Or Historical Lessons

Write to:

- [docs/registers](/Users/nihao/Documents/Playground/document-ops-system/docs/registers)

### Trace Or Replay Navigation

Write to:

- [TRACE_INDEX_MODEL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/TRACE_INDEX_MODEL.md)
- [CODEBASE_INDEX_MODEL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/CODEBASE_INDEX_MODEL.md)

## Promotion Rule

When a valid improvement appears during work:

1. record it locally
2. classify it by layer
3. promote it into the correct long-lived file
4. update the roadmap if it changes product direction
