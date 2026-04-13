# Agent CLI Reference Index

## Purpose

This index maps the local reference corpus used to compare `Document Operations
System` against agentic CLI systems, especially:

- OpenAI Codex CLI
- Anthropic Claude Code

It exists to support:

- runtime architecture planning
- memory-system redesign
- harness evolution
- prompt and subagent design
- approval and sandbox policy design
- product benchmarking

## Storage Boundary

These references are intentionally separated from active platform code:

- official sources:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official`
- secondary/community sources:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/secondary`
- local research notes:
  - `/Users/nihao/Documents/Playground/document-ops-system/docs/research`

Do not mix these repositories into active platform implementation paths.

## Official Repositories

### OpenAI Codex

- local path:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex`
- upstream:
  - [openai/codex](https://github.com/openai/codex)
- pinned revision:
  - `39cc85310fbb1c4d04034e596cd7420090875799`
- most relevant local files:
  - [AGENTS.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex/AGENTS.md)
  - [docs/agents_md.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex/docs/agents_md.md)
  - [docs/skills.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex/docs/skills.md)
  - [docs/config.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex/docs/config.md)
  - [docs/sandbox.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex/docs/sandbox.md)
  - [docs/slash_commands.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex/docs/slash_commands.md)
- why it matters:
  - project instruction layering via `AGENTS.md`
  - skills model
  - sandbox and approvals model
  - config and command surface

### Anthropic Claude Code

- local path:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code`
- upstream:
  - [anthropics/claude-code](https://github.com/anthropics/claude-code)
- pinned revision:
  - `9772e13f820002c9730af67a2409702799c7ddc6`
- most relevant local files:
  - [README.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code/README.md)
  - [plugins/README.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code/plugins/README.md)
  - [examples/settings/README.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code/examples/settings/README.md)
  - [examples/settings/settings-strict.json](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code/examples/settings/settings-strict.json)
  - [plugins/plugin-dev/skills/agent-development/references/agent-creation-system-prompt.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code/plugins/plugin-dev/skills/agent-development/references/agent-creation-system-prompt.md)
  - [plugins/plugin-dev/skills/agent-development/references/system-prompt-design.md](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code/plugins/plugin-dev/skills/agent-development/references/system-prompt-design.md)
- why it matters:
  - plugin structure
  - hooks / commands / skills / agents separation
  - managed settings and strict policy examples
  - public prompt-design artifacts for agent creation

## Official Documentation References

### Codex

- [Codex CLI docs](https://developers.openai.com/codex/cli)
- [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [Skills guide](https://developers.openai.com/codex/skills)
- [Security and approvals](https://developers.openai.com/codex/security)

### Claude Code

- [Overview](https://code.claude.com/docs/en/overview)
- [Settings](https://code.claude.com/docs/en/settings)
- [Memory](https://code.claude.com/docs/en/memory)
- [Sub-agents](https://code.claude.com/docs/en/sub-agents)
- [CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Security](https://code.claude.com/docs/en/security)

### Supporting Runtime References

- [OpenAI Agents SDK sessions](https://openai.github.io/openai-agents-python/sessions/)
- [OpenAI Agents SDK handoffs](https://openai.github.io/openai-agents-python/handoffs/)
- [OpenAI Agents SDK guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [LangGraph durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- [LangChain human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [CrewAI memory](https://docs.crewai.com/en/concepts/memory)
- [Google ADK workflow agents](https://google.github.io/adk-docs/agents/workflow-agents/)

## Secondary Repositories

These are useful for discovery and ecosystem scanning, but not as authority:

- [awesome-codex-cli](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/secondary/awesome-codex-cli)
  - upstream: [milisp/awesome-codex-cli](https://github.com/milisp/awesome-codex-cli)
  - pinned revision: `9427d9b422c0b6f90ff35f6b04e39e2c5bb5398c`
- [awesome-claude-code](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/secondary/awesome-claude-code)
  - upstream: [jqueryscript/awesome-claude-code](https://github.com/jqueryscript/awesome-claude-code)
  - pinned revision: `1c8868b4b3a1583a9dec87945233d0ef519a854a`
- [claude-code-best-practice](/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/secondary/claude-code-best-practice)
  - upstream: [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)
  - role: secondary workflow and memory-pattern reference
  - evaluation:
    - [CLAUDE_CODE_BEST_PRACTICE_EVALUATION.md](/Users/nihao/Documents/Playground/document-ops-system/docs/research/CLAUDE_CODE_BEST_PRACTICE_EVALUATION.md)

## Prompt-Like Artifact Availability

### Publicly available now

- Codex project instructions via `AGENTS.md`
- Codex docs for skills, config, sandbox, commands
- Claude Code plugin examples, agent examples, hook examples
- Claude plugin-dev prompt-design references
- Claude managed settings examples

### Not publicly equivalent

- Claude Code core internal system prompt is not exposed as an official public
  source in the same way project/plugin prompt-like artifacts are
- therefore, architecture borrowing should focus on:
  - runtime structure
  - memory layering
  - settings hierarchy
  - skills / commands / agent triggers
  - hooks and approval policy

## Next Reading Order

1. [AGENT_RUNTIME_BENCHMARK_FRAMEWORK.md](/Users/nihao/Documents/Playground/document-ops-system/docs/research/AGENT_RUNTIME_BENCHMARK_FRAMEWORK.md)
2. [MEMORY_AND_HARNESS_EVOLUTION_NOTE.md](/Users/nihao/Documents/Playground/document-ops-system/docs/research/MEMORY_AND_HARNESS_EVOLUTION_NOTE.md)
3. Codex `AGENTS.md`
4. Claude `plugins/README.md`
5. Claude settings examples
