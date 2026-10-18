# OfficeX

[![CI](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Document operations infrastructure for AI agents and humans.** Deterministic execution, three verification tracks, extensible through profiles.

[中文文档 / Chinese Documentation](README_CN.md)

---

## What is OfficeX?

OfficeX is a **document operations platform**: the reliable execution layer that AI agents and humans call to build, modify, verify, and audit Word documents.

It is **not** a chatbot. It is **not** trying to be intelligent. It is the part that makes sure the document is correct after the intelligent part is done thinking.

**The core contract:**
- You give OfficeX a structured instruction → it executes it deterministically
- You give OfficeX a document → it reports what is wrong, structurally, semantically and visually
- You give OfficeX a profile → it builds and checks against that paper size, font and style system

**What it solves:** when AI generates large documents through code, the results suffer from layout drift, style corruption, broken pagination, phantom references, and figure-text misalignment. Many of these are invisible to text/XML inspection. OfficeX checks the document from three directions (see [Verification](#three-verification-tracks)).

## Try it in a minute (no API key)

```bash
git clone https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc.git
cd OfficeX-an-AI-agents-for-doc
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock.txt && pip install -e .

# 1. Build the bundled demo document from manifests (deterministic, no AI)
officex task run-docx-mvp --sandbox-root sandboxes --run-id demo
DOC=sandboxes/demo/candidate/minimal_writer_demo.docx

# 2. Structural + semantic checks (no LibreOffice needed)
officex validate --docx "$DOC"

# 3. Visual checks: render every page to PNG (needs LibreOffice)
officex audit visual --candidate-docx "$DOC" --output-dir sandboxes/demo/visual

# 4. Page-by-page visual diff of two versions (needs LibreOffice)
officex diff --a "$DOC" --b "$DOC" --output-dir sandboxes/demo/diff
```

Add `--as-json` to any of these for machine-readable output. The demo is a single short page, so step 3 reports a `large-white-gap` warning for it. `sandboxes/` is git-ignored.

## How It's Used

### By AI agents (primary use case)

Agents call OfficeX as a CLI tool or over MCP and read JSON results:

```bash
officex validate --docx report.docx --as-json                               # structural + semantic
officex audit visual --candidate-docx report.docx --output-dir /tmp/audit --as-json
officex diff --a v1.docx --b v2.docx --output-dir /tmp/diff --as-json
officex task apply-patch-bundle --patch-bundle patch.json \
  --candidate-docx report.docx --anchor-snapshot anchors.json --as-json     # dry-run by default
```

Exit codes are meaningful for `validate`, `audit visual` and `diff`: `0` clean, `1` errors found (or pages differ, for `diff`), `2` usage error or LibreOffice missing.

**MCP** (Claude Desktop, Cursor, any MCP client). Use the absolute path to the `officex` in your virtualenv, because MCP clients do not activate it for you (`which officex` prints it):

```json
{
  "mcpServers": {
    "officex": {
      "command": "/absolute/path/to/OfficeX-an-AI-agents-for-doc/.venv/bin/officex",
      "args": ["serve"]
    }
  }
}
```

MCP tools: `officex_validate`, `officex_audit_visual`, `officex_diff`, `officex_profile_list`, `officex_doctor`, and the AI-backed `officex_generate`, `officex_generate_long`, `officex_edit`.

### By humans (standalone, needs an API key)

```bash
officex generate --prompt "Write a project proposal" --model qwen-plus
officex generate-long --outline my_outline.yml --model qwen-plus
officex edit --docx report.docx --instruction "Expand section 3" --model qwen-plus
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Interface Layer                          │
│                                                                 │
│  CLI (officex commands)     --as-json for machine consumption   │
│  MCP Server (officex serve) tools for Claude Desktop / Cursor   │
│  Skill doc (skills/)        integration guide for AI agents     │
├─────────────────────────────────────────────────────────────────┤
│                       Contract Layer                            │
│                                                                 │
│  Manifests    baseline, sections, figures, build source         │
│  Contracts    write_contract, layout_contract, template_profile │
│  Profiles     switchable paper/font/style configurations        │
│  Constitution 27 articles governing platform behavior           │
├─────────────────────────────────────────────────────────────────┤
│                      Execution Layer                            │
│                                                                 │
│  Writer       paragraphs, images, tables, AI code blocks        │
│  Patch Engine bounded paragraph-level mutations with anchors    │
│  Editor       AI proposes replace/insert/delete operations,     │
│               applied to a copy, then verified                  │
│  Assembler    manifest → block assembly → writer                │
│  Long Gen     outline → section-by-section with interleaved     │
│               review and prior-section context                  │
├─────────────────────────────────────────────────────────────────┤
│                    Verification Layer                           │
│                                                                 │
│  Structural   page geometry, style contract, image fit,         │
│               direct-formatting overrides                       │
│  Semantic     citation ↔ bibliography, figure/table numbering,  │
│               appendix and section cross-references, figure     │
│               placement, terminology consistency                │
│  Visual       LibreOffice headless → PNG → blank pages,         │
│               aspect ratio, white gaps                          │
├─────────────────────────────────────────────────────────────────┤
│                        Trace Layer                              │
│                                                                 │
│  run-docx-mvp writes a task packet, event log and stage history │
│  per run; review ledgers and checkpoints are separate commands  │
└─────────────────────────────────────────────────────────────────┘
```

## Three Verification Tracks

| Track | What it checks | How | Run by |
|-------|---------------|-----|--------|
| **Structural** | Page geometry, style contract, image fit, direct-formatting overrides | python-docx / OOXML inspection against the active profile | `validate`, `generate`, `edit`, `task run-docx-mvp` |
| **Semantic** | Citations vs bibliography, figure/table numbering, appendix and section cross-references, figure placement, terminology | Pattern matching on document text | `validate` |
| **Visual** | Blank pages, aspect ratio, large white gaps | LibreOffice → PDF → PNG → Pillow | `audit visual`, `diff`, `generate`, `edit` |

To check a document completely, run `officex validate` and `officex audit visual`. Each track states its own scope: structural checks never claim visual correctness, and semantic checks are pattern-based (they report warnings, not proof that the content is right).

## Commands

| Command | Description | Needs |
|---------|-------------|-------|
| `officex` | Banner + environment scan | |
| `officex validate` | Structural + semantic checks for any docx | |
| `officex audit visual` | Render to PNG + visual QA | LibreOffice |
| `officex diff` | Page-by-page visual comparison of two docx | LibreOffice |
| `officex task run-docx-mvp` | Build the bundled demo docx from manifests in a sandbox | |
| `officex task apply-patch-bundle` | Apply anchored paragraph patches (dry-run by default) | |
| `officex profile list/use/create/validate` | Manage document profiles | |
| `officex serve` | Start the MCP server (stdio) | |
| `officex doctor` | Environment readiness check | |
| `officex init` | Create a working folder with an example outline | |
| `officex generate` | Prompt → AI → docx → structural + visual checks | API key |
| `officex generate-long` | Outline → section-by-section AI → docx → checks | API key |
| `officex edit` | AI edit of an existing docx → checks | API key |
| `officex provider list`, `officex agent list` | Inspect provider and agent catalogs | |
| `officex trace checkpoint --title "..."` | Write a trace checkpoint | |

Every command has `--help`. Commands that produce a report support `--as-json`. Runs write to the repository's `sandboxes/` directory (git-ignored) unless you pass `--sandbox-root` / `--output-dir`.

## Profiles

Profiles are switchable document configurations (paper, margins, font, styles):

```bash
officex profile list                                   # see profiles, * marks the active one
officex validate --docx report.docx --profile letter_business   # check against a profile without switching
officex profile use letter_business                    # switch to US Letter + Arial
officex profile create my_custom \
  --page-width 515.9 --page-height 728.5 \
  --font "Yu Gothic" --font-size 10.5                  # create a new one at runtime
```

`officex profile use` copies the profile's contracts over `manifests/*.yml` in your checkout, so it affects every later command (switch back with `officex profile use a4_academic`). Profiles define their own paragraph roles: the bundled `run-docx-mvp` demo source is written for `a4_academic`.

## AI Providers

AI commands use any OpenAI-compatible endpoint, configured through environment variables. The default model id is `qwen-plus`, so pass `--model` for other providers.

| Provider | Setup |
|----------|-------|
| OpenAI | `OFFICEX_PROVIDER_API_KEY=sk-...`, then `--model gpt-4o` (or another OpenAI model) |
| Alibaba DashScope | `OFFICEX_PROVIDER_API_KEY=sk-...` `OFFICEX_PROVIDER_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| DeepSeek | `OFFICEX_PROVIDER_API_KEY=sk-...` `OFFICEX_PROVIDER_BASE_URL=https://api.deepseek.com/v1`, then `--model deepseek-chat` |
| Local / self-hosted | `OFFICEX_PROVIDER_API_KEY=...` `OFFICEX_PROVIDER_BASE_URL=http://localhost:8080/v1`, plus `--model <your model>` |

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | macOS or Linux (CI runs on `macos-latest` and `ubuntu-latest`). Windows is untested |
| **Python** | 3.11 or 3.12 (both tested in CI) |
| **LibreOffice** | Optional. Needed for `audit visual`, `diff`, and the visual step of `generate`/`edit` |
| **API key** | Optional. Needed only for `generate`, `generate-long`, `edit` |

Install from a clone with `pip install -e .` as shown above. A PyPI package is not published yet; a regular (non-editable) install does not include the manifests and profiles.

## Constitution

OfficeX behavior is governed by [CONSTITUTION.md](CONSTITUTION.md): 27 articles across 8 domains.

1. **Authority**: manifests are law. Layers don't reach up.
2. **Execution**: sandbox before mutation. Verify before claiming. Degrade, don't block.
3. **Memory**: four-tier layered. Retrieval informs, never governs.
4. **Interaction**: weight determines dialogue. Never fabricate key inputs.
5. **Security**: content stays in boundaries. Secrets never touch disk.
6. **Extensibility**: configuration is dynamic. Skills are self-contained.
7. **Planning**: plan granularity matches complexity. Documents read like one author.
8. **Trace**: everything leaves a trail. Traces are replayable.

## Development

```bash
pip install -r requirements.lock.txt && pip install -e .
pytest -q
python -m tools.report_scaffold_v3.cli check-package
```

CI runs the test suite, the package integrity check and a CLI smoke test on macOS and Ubuntu with Python 3.11 and 3.12 against `requirements.lock.txt`, plus a weekly run against the latest allowed dependency versions.

| Branch | Purpose |
|--------|---------|
| `main` | Stable; CI must pass |
| `dev` | Active development |

## License

MIT
