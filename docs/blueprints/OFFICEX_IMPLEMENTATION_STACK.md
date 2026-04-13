---
doc_id: officex_implementation_stack
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# OfficeX Implementation Stack

## MVP Platform Choice

The current recommended MVP stack is:

- app shell: `Electron`
- frontend: `TypeScript + React`
- embedded editor surface: `ONLYOFFICE Docs Community Edition`
- local core runtime: `Python`
- future migration target for selected core subsystems: `Rust`

## Why This Stack

### Electron For The First Desktop Shell

- easier macOS-first desktop packaging than introducing Rust shell complexity
  immediately
- straightforward embedding of web-based editor surfaces
- good fit for TypeScript-heavy app UI and review canvas work
- keeps the MVP focused on document runtime correctness rather than shell
  experimentation

### TypeScript Frontend

- strong ecosystem for complex app state, layout, and collaborative UI
- large ecosystem for document-like canvas interactions and advanced UI patterns
- natural fit for Electron and future web companion reuse

### Python Runtime First

- matches current codebase history and existing runtime assets
- already owns the active CLI and document-engineering modules
- fast iteration for OOXML, audit, parsing, and orchestration work

### Rust Later

Rust remains the preferred long-term target for:

- selected performance-critical subsystems
- hardened local services
- potentially a future app shell or native document-processing core

Rust is not the recommended first move for the MVP because it would slow the
first complete loop.

## macOS-First Delivery Rule

The first supported local platform is:

- `macOS`

This affects:

- packaging and signing priorities
- local file access assumptions
- editor embedding tests
- keychain and secrets handling

## Provider Model

The app should support user-provided AI APIs through a provider abstraction.

Minimum provider categories:

- OpenAI-compatible chat provider
- Anthropic-style chat provider
- compatible local or self-hosted provider

Provider handling rules:

- API keys stay outside repo-tracked files
- desktop app stores secrets in the OS keychain where possible
- runtime sees provider capability metadata, not raw secrets by default
- provider adapters are isolated from document execution code

## Decoupling Rules

Keep these subsystems separated:

1. UI surface
2. agent orchestration
3. deterministic `docx` execution
4. visual audit
5. provider adapters
6. memory and retrieval
7. trace and publication

No one subsystem should be able to silently mutate all others.

## MVP Delivery Flow

1. desktop app loads local workspace
2. user imports prompt, rubric, template, and source files
3. orchestrator builds a plan
4. AI providers generate text, review output, or generation code
5. Python runtime executes bounded `docx` mutation
6. visual and structural audit runs
7. user accepts or rejects patches in the app
8. verified candidate is exported and traced
