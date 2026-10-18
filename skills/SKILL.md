# OfficeX Skill

Use this skill when you need to generate, validate, or audit Word (.docx) documents programmatically.

## What OfficeX Can Do

- **Validate** any docx structurally (styles, fonts, page geometry, image fit, overrides) and semantically (citations, figure/table numbering, cross-references, terminology)
- **Visual audit** by rendering to PNG and checking layout
- **Diff** two documents page by page, visually
- **Apply patches** to existing documents deterministically, through anchors
- **Generate and edit** documents with an AI provider (needs an API key)

## Quick Reference

```bash
# Structural + semantic checks on any docx (no API key, no LibreOffice)
officex validate --docx report.docx --as-json

# Render to PNG and check the pages (needs LibreOffice)
officex audit visual --candidate-docx report.docx --output-dir ./audit --as-json

# Visual page-by-page diff of two versions (needs LibreOffice)
officex diff --a v1.docx --b v2.docx --output-dir ./diff --as-json

# Build the bundled demo document from manifests (deterministic)
officex task run-docx-mvp --run-id my-run --sandbox-root /tmp/sandbox --as-json

# Apply a patch bundle to a document (dry-run by default; add --apply to write)
officex task apply-patch-bundle --patch-bundle patch.json --candidate-docx doc.docx --anchor-snapshot anchors.json --as-json

# Generate a document from a prompt (needs an API key; default model is qwen-plus)
officex generate --prompt "Write a project proposal about X" --model qwen-plus --output-dir ./output --as-json

# Check environment readiness
officex doctor --as-json
```

## Environment Requirements

- Python 3.11 or 3.12, installed from a clone with `pip install -r requirements.lock.txt && pip install -e .`
- LibreOffice (optional, for `audit visual` and `diff`): `brew install --cask libreoffice` on macOS, your package manager on Linux
- API key for AI features: `export OFFICEX_PROVIDER_API_KEY="your-key"`
- Base URL for providers other than OpenAI: `export OFFICEX_PROVIDER_BASE_URL="https://..."`, and pass `--model`

## How to Integrate

### As an MCP server

Run `officex serve` (stdio). Point your MCP client at the absolute path of the `officex` binary in the virtualenv. Tools: `officex_validate`, `officex_audit_visual`, `officex_diff`, `officex_profile_list`, `officex_doctor`, `officex_generate`, `officex_generate_long`, `officex_edit`. A missing input file or a failed render comes back as an MCP error result.

### As a CLI tool called by your agent

Report-producing commands support `--as-json`. Your agent can:

1. Call `officex generate --prompt "..." --as-json` to create documents, or build them yourself
2. Parse the JSON response to get the output path and status
3. Call `officex validate --docx <path> --as-json` for structural and semantic findings
4. Call `officex audit visual --candidate-docx <path> --output-dir <dir> --as-json` and read the PNG files to inspect the pages
5. If issues are found, regenerate or apply patches, then `officex diff` the versions

### Exit codes

For `validate`, `audit visual` and `diff`: `0` clean, `1` errors found (or pages differ, for `diff`), `2` usage error or LibreOffice missing. Usage errors print a short message on stderr, never a traceback.

### JSON output schema for `generate`

```json
{
  "run_id": "gen-20260501-221650",
  "status": "success",
  "output_docx": "/path/to/output.docx",
  "page_count": 3,
  "png_paths": ["/path/to/visual/page-1.png", "..."],
  "ai_model": "qwen-plus",
  "ai_tokens": {"prompt_tokens": 1019, "completion_tokens": 658, "total_tokens": 1677},
  "validation_errors": 0,
  "validation_warnings": 0,
  "visual_findings": 0,
  "error_message": ""
}
```

### Status codes

- `success`: document generated and verified
- `ai_failed`: AI provider call or response parsing failed
- `build_failed`: document construction failed
- `validation_warnings`: document built but has validation issues

## Non-negotiable: Render Before Shipping

You do not "know" a document is correct until you have rendered it to PNG and inspected the pages. Text/XML checks will miss layout defects.

`officex generate` and `officex edit` run structural and visual checks automatically. If you build documents yourself, run `officex validate` and `officex audit visual`.
