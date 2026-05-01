# OfficeX

[![CI](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**AI-powered document operations platform.** Generate, validate, and audit Word documents through a CLI that works standalone or as a skill for AI agents.

[中文文档 / Chinese Documentation](README_CN.md)

---

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable release. Everything here works. |
| `dev` | Active development. May contain incomplete features. |

## What Works Out of the Box (no API key needed)

These commands work immediately after install:

```bash
officex                              # Brand banner + environment scan
officex init                         # Create a workspace
officex doctor --as-json             # Environment readiness check
officex profile list                 # List document profiles
officex profile create my_profile    # Create a new profile
officex task run-docx-mvp            # Deterministic docx from manifests
officex audit visual --candidate-docx file.docx  # Visual QA (needs LibreOffice)
```

## AI-Powered Commands (needs API key)

These commands require an OpenAI-compatible API key:

```bash
export OFFICEX_PROVIDER_API_KEY="your-key"
export OFFICEX_PROVIDER_BASE_URL="https://your-provider/v1"

officex generate --prompt "..."                    # Short document
officex generate-long --outline outlines/plan.yml  # Long document
```

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | macOS 10.9+ (Intel), macOS 11+ (Apple Silicon), Linux (glibc 2.28+, x86_64/aarch64) |
| **Python** | 3.11+ |
| **LibreOffice** | Optional. Required for visual audit (PNG rendering) |
| **API Key** | Optional. Required for AI-powered `generate` command. Any OpenAI-compatible endpoint |

> Windows is not currently supported. All native dependencies (pymupdf, lxml, numpy, Pillow) provide wheels for macOS and Linux.

## What is OfficeX?

OfficeX is an **AI agent platform** whose first vertical is document operations. It solves a fundamental problem: when AI generates large documents directly through Python, the results suffer from layout issues, style drift, broken pagination, and table overflow — problems invisible to text/XML inspection.

OfficeX separates concerns:
- **AI** generates content (text, structure, review findings)
- **Deterministic program code** owns document structure (styles, layout, numbering, page geometry)
- **Dual-track verification** (structural + visual) proves the output is correct

The platform is designed to be extended with **Skills** for different document scenarios. The current MVP validates the full pipeline using academic document generation as the test case.

## Workflow

```
                    ┌─────────────────────┐
                    │   User / Agent       │
                    │   provides prompt    │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   AI Provider        │
                    │   generates content  │
                    │   as structured JSON │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Build Source       │
                    │   manifest-driven    │
                    │   block assembly     │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Writer             │
                    │   deterministic docx │
                    │   generation         │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │                               │
    ┌─────────▼─────────┐          ┌──────────▼──────────┐
    │ Structural         │          │ Visual               │
    │ Validation         │          │ Audit                │
    │ - page geometry    │          │ - LibreOffice render │
    │ - style contract   │          │ - blank page check   │
    │ - image fit        │          │ - aspect ratio       │
    │ - override detect  │          │ - white gap detect   │
    └─────────┬─────────┘          └──────────┬──────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Both pass?         │
                    │   → Verified .docx   │
                    │   + page PNGs        │
                    └─────────────────────┘
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Surface Layer                                               │
│  CLI (officex commands)  |  Skill interface (--as-json)      │
├─────────────────────────────────────────────────────────────┤
│  Contract Layer                                              │
│  manifests/  (baseline, write_contract, template_profile,    │
│              layout_contract, provider_catalog, agent_catalog)│
│  All behavior driven by declarative manifests                │
├─────────────────────────────────────────────────────────────┤
│  Execution Layer                                             │
│  manifest_loader → section_assembler → writer → docx         │
│  AI generates content; program code owns structure           │
├─────────────────────────────────────────────────────────────┤
│  Verification Layer                                          │
│  Structural: validation/ (page_setup, style, image, override)│
│  Visual: LibreOffice headless → PNG → Pillow checks          │
├─────────────────────────────────────────────────────────────┤
│  Runtime Layer                                               │
│  provider_adapter (OpenAI-compatible dispatch)               │
│  prompt_runtime (role composition + cognition layer)         │
│  agent_runtime (orchestrator, writer, validation_engineer...)│
├─────────────────────────────────────────────────────────────┤
│  Trace Layer                                                 │
│  Checkpoints, stage history, event logs, review ledgers      │
│  Platform-level memory for agent operations                  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install

```bash
git clone https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc.git
cd OfficeX-an-AI-agents-for-doc

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
pip install -e .
```

### 2. Check environment

```bash
officex
```

Auto-scans Python, LibreOffice, dependencies, and API key status.

### 3. (Optional) Install LibreOffice for visual audit

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt install libreoffice
```

### 4. Generate a document

```bash
export OFFICEX_PROVIDER_API_KEY="your-api-key"
export OFFICEX_PROVIDER_BASE_URL="https://your-provider/v1"

officex generate \
  --prompt "Write a project proposal for a mobile study scheduler app" \
  --model qwen-plus \
  --output-dir ./my-proposal
```

Output:
```
Generated: ./my-proposal/gen-20260501-221650.docx
Model: qwen-plus | Tokens: {'prompt_tokens': 1019, 'completion_tokens': 658, 'total_tokens': 1677}
Validation: 0 error(s), 0 warning(s)
Visual: 1 page(s), 0 finding(s)
```

## Use as an AI Agent Skill

OfficeX is designed to be called by AI agents (Codex, Claude Code, Hermes, etc.) as a document operations tool.

**Skill documentation:** See [`skills/SKILL.md`](skills/SKILL.md) for the complete integration guide.

All commands support `--as-json` for machine-parseable output:

```bash
# Your agent calls OfficeX
officex generate --prompt "..." --model qwen-plus --output-dir /tmp/task-123 --as-json

# Parse JSON result
# {
#   "status": "success",
#   "output_docx": "/tmp/task-123/gen-xxx.docx",
#   "page_count": 3,
#   "validation_errors": 0
# }
```

## Commands

| Command | Description |
|---------|-------------|
| `officex` | Banner + environment scan |
| `officex generate --prompt "..."` | Prompt → AI → docx → validate → visual QA |
| `officex doctor` | Full environment readiness check |
| `officex audit visual --candidate-docx f.docx` | Render to PNG + visual QA |
| `officex task run-docx-mvp` | Deterministic docx from manifests |
| `officex task apply-patch-bundle` | Apply deterministic patches |
| `officex provider list` | List configured providers |
| `officex prompt show --role orchestrator` | Show composed role prompt |
| `officex agent list` | List registered agent roles |
| `officex trace checkpoint` | Create a trace checkpoint |

## Supported Providers

Any OpenAI-compatible endpoint works:

| Provider | Setup |
|----------|-------|
| OpenAI | `OFFICEX_PROVIDER_API_KEY=sk-...` |
| Alibaba DashScope | `OFFICEX_PROVIDER_API_KEY=sk-... OFFICEX_PROVIDER_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Local / self-hosted | `OFFICEX_PROVIDER_API_KEY=... OFFICEX_PROVIDER_BASE_URL=http://localhost:8080/v1` |

## Development

```bash
.venv/bin/pytest -q          # 183 tests
officex doctor --as-json     # Environment check
```

## License

MIT
