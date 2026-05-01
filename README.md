# OfficeX

**AI-powered document operations platform.** Generate, validate, and audit Word documents through a CLI that works standalone or as a skill for AI agents.

[中文文档 / Chinese Documentation](README_CN.md)

## What It Does

```
Your prompt  -->  AI generates content  -->  OfficeX builds .docx  -->  Structural + Visual QA  -->  Verified document
```

OfficeX turns document creation into an engineered pipeline:

- **Generate**: Give it a prompt, get a properly formatted Word document
- **Validate**: Structural checks (styles, fonts, page geometry, image fit)
- **Visual Audit**: Renders to PNG via LibreOffice, checks for blank pages, layout gaps, aspect ratio issues
- **Deterministic**: Same input always produces same output. AI generates content, but program code owns document structure

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

This shows the brand banner with auto-detected environment status:

```
╭──────────────────────────────────────────────────────────╮
│  OfficeX  Document Operations System                      │
│  v0.1.0  |  Python 3.11.15                                │
╰──────────────────────────────────────────────────────────╯
                       Environment
┌────────────────┬────────┬────────────────────────────────┐
│ Python         │   OK   │ 3.11.15                        │
│ LibreOffice    │   OK   │ visual audit available         │
│ Core deps      │   OK   │ all present                    │
│ API key        │   --   │ set OFFICEX_PROVIDER_API_KEY   │
└────────────────┴────────┴────────────────────────────────┘
```

### 3. Optional: Install LibreOffice (for visual audit)

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt install libreoffice
```

### 4. Generate a document

```bash
export OFFICEX_PROVIDER_API_KEY="your-api-key"
export OFFICEX_PROVIDER_BASE_URL="https://your-provider/v1"  # OpenAI-compatible endpoint

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

The output directory contains:
- `*.docx` — Final Word document
- `ai_response.txt` — Raw AI output
- `build_source.json` — Parsed document structure
- `validation.json` — Structural validation report
- `visual/page-*.png` — Rendered page images

## Commands Reference

| Command | Description |
|---------|-------------|
| `officex` | Show banner + environment scan |
| `officex generate --prompt "..."` | End-to-end: prompt to verified docx |
| `officex doctor` | Full environment readiness check |
| `officex audit visual --candidate-docx file.docx` | Render to PNG + visual QA |
| `officex task run-docx-mvp` | Deterministic docx from manifests |
| `officex task apply-patch-bundle` | Apply deterministic patches |
| `officex provider list` | List configured AI providers |
| `officex provider build-request` | Build provider request envelope |
| `officex prompt show --role orchestrator` | Show composed role prompt |
| `officex agent list` | List registered agent roles |
| `officex trace checkpoint` | Create a trace checkpoint |

All commands support `--as-json` for machine-readable output.

## Use as an AI Agent Skill

OfficeX is designed to be called by other AI agents (Codex, Claude Code, Hermes, etc.) as a document operations tool:

```bash
# Agent calls OfficeX to generate a document
officex generate --prompt "..." --model qwen-plus --output-dir /tmp/task-123 --as-json

# Agent calls OfficeX to validate an existing document
officex audit visual --candidate-docx report.docx --output-dir /tmp/audit-123 --as-json

# Agent reads JSON output to decide next steps
```

The `--as-json` flag ensures all output is machine-parseable. Agents can:
1. Call `officex generate` to create documents from natural language
2. Call `officex audit visual` to verify document quality
3. Parse JSON results to determine success/failure
4. Iterate: fix issues and regenerate

## Supported Providers

OfficeX uses the OpenAI-compatible chat API. Any provider with a compatible endpoint works:

| Provider | Configuration |
|----------|--------------|
| OpenAI | `OFFICEX_PROVIDER_API_KEY=sk-...` |
| Anthropic (via proxy) | `OFFICEX_PROVIDER_API_KEY=... OFFICEX_PROVIDER_BASE_URL=...` |
| Alibaba DashScope | `OFFICEX_PROVIDER_API_KEY=sk-... OFFICEX_PROVIDER_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Local/self-hosted | `OFFICEX_PROVIDER_API_KEY=... OFFICEX_PROVIDER_BASE_URL=http://localhost:8080/v1` |

## Architecture

```
Contract Layer    manifests/ (baseline, write_contract, template_profile, layout_contract)
                  All behavior driven by declarative manifests, nothing hardcoded
                       |
Execution Layer   manifest_loader -> assembler -> writer -> docx
                  AI generates content; deterministic code owns document structure
                       |
Verification      Structural: validation/ (page_setup, style, image_fit, overrides)
                  Visual: LibreOffice headless -> PNG -> Pillow checks
                  Both must pass for the document to be considered correct
                       |
Runtime Layer     provider_adapter (OpenAI-compatible dispatch)
                  prompt_runtime (role composition with cognition layer)
                  agent_runtime (6 runtime roles)
                       |
Trace Layer       Checkpoints, stage history, event logs, review ledgers
                  Platform-level memory, not just file tracking
```

## Development

```bash
# Run tests
.venv/bin/pytest -q

# Run specific test
.venv/bin/pytest tests/test_golden_path.py -v

# Check package integrity
officex doctor --as-json
```

## License

MIT
