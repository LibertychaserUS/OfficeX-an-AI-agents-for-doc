# OfficeX Skill

Use this skill when you need to generate, validate, or audit Word (.docx) documents programmatically.

## What OfficeX Can Do

- **Generate documents** from natural language prompts
- **Validate** document structure (styles, fonts, page geometry, image fit)
- **Visual audit** by rendering to PNG and checking layout
- **Apply patches** to existing documents deterministically
- **Inspect** task artifacts and provider configurations

## Quick Reference

```bash
# Generate a document from a prompt
officex generate --prompt "Write a project proposal about X" --model qwen-plus --output-dir ./output --as-json

# Validate an existing document visually
officex audit visual --candidate-docx report.docx --output-dir ./audit --as-json

# Run the deterministic generation pipeline from manifests
officex task run-docx-mvp --run-id my-run --sandbox-root /tmp/sandbox --as-json

# Apply a patch bundle to a document
officex task apply-patch-bundle --patch-bundle patch.json --candidate-docx doc.docx --anchor-snapshot anchors.json --as-json

# Check environment readiness
officex doctor --as-json
```

## Environment Requirements

- Python 3.11+
- LibreOffice (optional, for visual audit): `brew install --cask libreoffice`
- API key for AI features: `export OFFICEX_PROVIDER_API_KEY="your-key"`
- Base URL for non-OpenAI providers: `export OFFICEX_PROVIDER_BASE_URL="https://..."`

## How to Integrate

### As a CLI tool called by your agent

All commands support `--as-json` for machine-readable output. Your agent can:

1. Call `officex generate --prompt "..." --as-json` to create documents
2. Parse the JSON response to get the output path and status
3. Call `officex audit visual --candidate-docx <path> --as-json` to verify quality
4. Read the PNG files to visually inspect the result
5. If issues found, regenerate or apply patches

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

- `success` — Document generated and verified
- `ai_failed` — AI provider call or response parsing failed
- `build_failed` — Document construction failed
- `validation_warnings` — Document built but has validation issues

## Non-negotiable: Render Before Shipping

You do not "know" a document is correct until you have rendered it to PNG and inspected the pages. Text/XML checks will miss layout defects.

The `officex generate` command does this automatically. If you build documents manually, always follow up with `officex audit visual`.
