# OfficeX Development Roadmap

## Branch Strategy
- `main`: Stable release. Only merge from dev after full test pass.
- `dev`: Active development. All new work lands here first.

## Phase 1: Core Completeness (Near-term)

### 1.1 `officex edit` — Edit existing documents
- Load an existing .docx
- AI reviews and suggests changes
- Apply changes as bounded patches
- Structural + visual verification after edits
- **Priority: High** — Completes the create/edit/validate lifecycle

### 1.2 `officex diff` — Visual document comparison
- Render two .docx files to PNG
- Per-page image diff (highlight changed regions)
- JSON report of differences
- **Priority: High** — Enables regression detection

### 1.3 MCP Server mode
- `officex serve` starts a JSON-RPC server (stdio or HTTP)
- Exposes generate, validate, audit, profile as MCP tools
- Enables Claude Desktop / Cursor / any MCP client integration
- **Priority: High** — Major distribution channel

### 1.4 PyPI publish
- `pip install officex` works
- Entry point already defined in pyproject.toml
- Need: clean build, test on fresh venv, publish to PyPI
- **Priority: High** — Reduces adoption friction to zero

## Phase 2: Platform Depth (Mid-term)

### 2.1 Multi-agent orchestration
- Plan agent generates dependency graph between sections
- Independent sections can be generated in parallel
- Dependent sections generated serially with full context
- Reviewer agent interleaves during generation (every N sections)
- **Depends on:** Long generate working (done)

### 2.2 Interleaved review during generation
- After every N sections, a review pass checks coherence
- Terminology drift, tone shift, argument gaps detected early
- Revisions applied before continuing generation
- **Constitution Article 24**

### 2.3 Memory implementation (4-tier)
- Layer 1 System: file-backed, version-tracked contracts
- Layer 2 Session: structured run state, append-only
- Layer 3 User: preferences persisted to ~/.officex/user.yml
- Layer 4 Retrieval: SQLite FTS5 index over past runs
- **Constitution Articles 9-12**

### 2.4 Executable review criteria
- Parse review_criteria for auto-checkable rules
- "All paragraphs under 200 words" → automatic
- "Professional tone" → stays as AI review
- Split criteria into deterministic vs AI-judged

### 2.5 Table generation in writer
- writer.py learns to create Word tables
- DXA geometry normalization (ref: CodeX table_geometry.py)
- Cell margins, header rows, column width by content type

## Phase 3: Ecosystem (Longer-term)

### 3.1 Streaming output (independent platform mode)
- CoT-style progress display during generation
- Section-by-section streaming as each completes
- Only in platform mode; skill mode returns complete results

### 3.2 Multi-language document awareness
- Profile includes language/locale settings
- Prompt templates adapt to document language
- Font selection aware of CJK requirements

### 3.3 Version tracking
- Document version history within workspace
- `officex diff v1 v2` compares versions
- Change log per document

### 3.4 Skill marketplace integration
- Publish OfficeX skills to skills.sh / agentskills.io
- Consume external skills (chart generation, data viz)

### 3.5 Skill documentation (layered)
```
skills/
├── SKILL.md              # Root entry + routing
├── tasks/
│   ├── generate.md
│   ├── validate_audit.md
│   ├── patch_revise.md
│   ├── profile_manage.md
│   └── inspect_diagnose.md
├── contracts/
│   ├── output_schema.md
│   └── error_codes.md
└── troubleshooting/
    ├── libreoffice.md
    └── provider.md
```

### 3.6 Community docs
- CONTRIBUTING.md
- CHANGELOG.md
- Usage screenshots / GIF demos
