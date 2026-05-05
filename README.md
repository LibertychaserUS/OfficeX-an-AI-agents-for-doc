# OfficeX

[![CI](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Document operations infrastructure for AI agents and humans.** Deterministic execution, triple-track verification, extensible through profiles and skills.

[中文文档 / Chinese Documentation](README_CN.md)

---

## What is OfficeX?

OfficeX is a **document operations platform** — the reliable execution layer that AI agents and humans call to build, modify, verify, and audit Word documents.

It is **not** a chatbot. It is **not** trying to be intelligent. It is the part that makes sure the document is correct after the intelligent part is done thinking.

**The core contract:**
- You give OfficeX a structured instruction → it executes precisely
- You give OfficeX a document → it tells you exactly what's wrong (structurally, visually, semantically)
- You give OfficeX a profile → it adapts to any paper size, font, style, language
- You give OfficeX a skill → it learns a new workflow without code changes

**What it solves:** When AI generates large documents through code, the results suffer from layout drift, style corruption, broken pagination, phantom references, and figure-text misalignment. These problems are invisible to text/XML inspection. OfficeX catches them through triple-track verification.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Interface Layer                           │
│                                                                  │
│  CLI (officex commands)     --as-json for machine consumption    │
│  MCP Server (officex serve) tools for Claude Desktop / Cursor    │
│  Skill docs (skills/)      integration guide for AI agents       │
├─────────────────────────────────────────────────────────────────┤
│                       Contract Layer                             │
│                                                                  │
│  Manifests    baseline, sections, figures, build source           │
│  Contracts    write_contract, layout_contract, template_profile  │
│  Profiles     runtime-switchable paper/font/style configurations │
│  Constitution 27 articles governing all platform behavior        │
│                                                                  │
│  All behavior is manifest-driven. Nothing is hardcoded.          │
├─────────────────────────────────────────────────────────────────┤
│                      Execution Layer                             │
│                                                                  │
│  Writer       paragraphs, images, tables, AI code blocks         │
│  Patch Engine bounded paragraph-level mutations with anchors     │
│  Editor       AI-driven edit → patch → verify cycle              │
│  Assembler    manifest → block assembly → writer                 │
│  Long Gen     outline → section-by-section with interleaved      │
│               review and prior-section context                   │
├─────────────────────────────────────────────────────────────────┤
│                    Verification Layer                             │
│                                                                  │
│  Track 1: Structural   page geometry, style contract, image fit, │
│           Validation   override detection                        │
│                                                                  │
│  Track 2: Visual       LibreOffice headless → PNG rendering →    │
│           Audit        blank page, aspect ratio, white gap check │
│                                                                  │
│  Track 3: Semantic     citation ↔ bibliography alignment,        │
│           Validation   figure/table numbering continuity,        │
│                        appendix references, section cross-refs,  │
│                        anchor proximity, terminology consistency │
│                                                                  │
│  All three tracks must pass. Each states its scope explicitly.   │
├─────────────────────────────────────────────────────────────────┤
│                     Extensibility Layer                           │
│                                                                  │
│  Profiles     officex profile create/use/list — any paper, font, │
│               style system, created at runtime by users or AI    │
│  Skills       user-defined workflow packages (SKILL.md + scripts)│
│  Criteria     auto-checkable rules + AI-judged rules, defined    │
│               per document, not hardcoded in platform            │
│  Providers    any OpenAI-compatible endpoint, env-var configured │
├─────────────────────────────────────────────────────────────────┤
│                        Trace Layer                               │
│                                                                  │
│  Checkpoints, stage history, event logs, review ledgers          │
│  Every operation leaves an auditable trail                       │
└─────────────────────────────────────────────────────────────────┘
```

## How It's Used

### By AI agents (primary use case)

AI agents call OfficeX as a tool/skill to execute document operations:

```bash
# Agent asks OfficeX to build a document from structured input
officex task run-docx-mvp --sandbox-root /tmp/run-1 --as-json

# Agent asks OfficeX to verify a document
officex audit visual --candidate-docx report.docx --output-dir /tmp/audit --as-json

# Agent asks OfficeX to diff two versions
officex diff --a v1.docx --b v2.docx --output-dir /tmp/diff --as-json
```

Via MCP (Claude Desktop, Cursor, etc.):
```json
{
  "mcpServers": {
    "officex": {
      "command": "officex",
      "args": ["serve"]
    }
  }
}
```

### By humans (standalone)

```bash
# Generate a document from a prompt (OfficeX calls AI for you)
officex generate --prompt "Write a project proposal" --model qwen-plus

# Generate a long document from an outline
officex generate-long --outline my_outline.yml --model qwen-plus

# Edit an existing document
officex edit --docx report.docx --instruction "Expand section 3" --model qwen-plus

# Switch document profile
officex profile use letter_business
```

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable release. Everything here works. |
| `dev` | Active development. May contain incomplete features. |

## What Works Out of the Box (no API key)

```bash
officex                              # Brand banner + environment scan
officex init                         # Create a workspace
officex doctor --as-json             # Environment readiness check
officex profile list                 # List document profiles
officex profile create my_profile    # Create a new profile at runtime
officex task run-docx-mvp            # Deterministic docx from manifests
officex audit visual --candidate-docx file.docx  # Visual QA (needs LibreOffice)
```

## AI-Powered Commands (needs API key)

```bash
export OFFICEX_PROVIDER_API_KEY="your-key"
export OFFICEX_PROVIDER_BASE_URL="https://your-provider/v1"

officex generate --prompt "..."                    # Short document
officex generate-long --outline plan.yml           # Long document
officex edit --docx file.docx --instruction "..."  # Edit existing document
```

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | macOS 10.9+ (Intel), macOS 11+ (Apple Silicon), Linux (glibc 2.28+, x86_64/aarch64) |
| **Python** | 3.11+ |
| **LibreOffice** | Optional. Required for visual audit (PNG rendering) |
| **API Key** | Optional. Required for AI-powered generate/edit commands. Any OpenAI-compatible endpoint |

## Quick Start

```bash
git clone https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc.git
cd OfficeX-an-AI-agents-for-doc

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
pip install -e .

officex                   # See environment status
officex doctor --as-json  # Full readiness check
```

## Commands

| Command | Description |
|---------|-------------|
| `officex` | Brand banner + environment scan |
| `officex init` | Initialize a workspace |
| `officex generate` | Short document: prompt → AI → docx → verify |
| `officex generate-long` | Long document: outline → section-by-section → verify |
| `officex edit` | Edit existing document with AI |
| `officex diff` | Visual comparison of two documents |
| `officex serve` | Start MCP server for AI agent integration |
| `officex doctor` | Environment readiness check |
| `officex audit visual` | Render to PNG + visual QA |
| `officex profile list/use/create` | Manage document profiles |
| `officex task run-docx-mvp` | Deterministic docx from manifests |
| `officex task apply-patch-bundle` | Apply deterministic patches |
| `officex provider list` | List configured AI providers |
| `officex agent list` | List registered agent roles |
| `officex trace checkpoint` | Create a trace checkpoint |

All commands support `--as-json` for machine-readable output.

## Profiles

Profiles are runtime-switchable document configurations (paper, font, style):

```bash
officex profile list                    # See available profiles
officex profile use letter_business     # Switch to US Letter + Arial
officex profile create my_custom \
  --page-width 515.9 --page-height 728.5 \
  --font "Yu Gothic" --font-size 10.5   # Create new at runtime
```

Nothing is hardcoded. Users and AI agents can create new profiles for any paper size, font, or style system.

## Triple-Track Verification

OfficeX verifies documents through three independent tracks:

| Track | What it checks | How |
|-------|---------------|-----|
| **Structural** | Page geometry, style contracts, image fit, override detection | python-docx inspection |
| **Visual** | Blank pages, aspect ratio, white gaps, layout drift | LibreOffice → PNG → Pillow |
| **Semantic** | Citation alignment, numbering continuity, appendix refs, section cross-refs, terminology | Pattern matching on content |

A document is not considered correct until all three tracks pass. Each track explicitly states its scope — structural checks never claim visual correctness, and vice versa.

## Constitution

OfficeX behavior is governed by [CONSTITUTION.md](CONSTITUTION.md) — 27 articles across 8 domains:

1. **Authority** — Manifests are law. Layers don't reach up.
2. **Execution** — Sandbox before mutation. Verify before claiming. Degrade, don't block.
3. **Memory** — Four-tier layered. Retrieval informs, never governs.
4. **Interaction** — Weight determines dialogue. Never fabricate key inputs.
5. **Security** — Content stays in boundaries. Secrets never touch disk.
6. **Extensibility** — Configuration is dynamic. Skills are self-contained.
7. **Planning** — Plan granularity matches complexity. Documents read like one author.
8. **Trace** — Everything leaves a trail. Traces are replayable.

## Supported Providers

Any OpenAI-compatible endpoint:

| Provider | Setup |
|----------|-------|
| OpenAI | `OFFICEX_PROVIDER_API_KEY=sk-...` |
| Alibaba DashScope | `OFFICEX_PROVIDER_API_KEY=sk-... OFFICEX_PROVIDER_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Local / self-hosted | `OFFICEX_PROVIDER_API_KEY=... OFFICEX_PROVIDER_BASE_URL=http://localhost:8080/v1` |

## Development

```bash
.venv/bin/pytest -q          # Run tests
officex doctor --as-json     # Environment check
```

## License

MIT
