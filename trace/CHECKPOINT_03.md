# CHECKPOINT_03

date: 2026-04-12

## Title

External agent-cli reference corpus established

## Summary

- A separated local reference corpus was created for agentic CLI comparison.
- Official repositories were cloned into:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/openai-codex`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/official/anthropic-claude-code`
- Secondary repositories were cloned into:
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/secondary/awesome-codex-cli`
  - `/Users/nihao/Documents/Playground/document-ops-system/references/agent_cli/secondary/awesome-claude-code`
- A machine-readable reference catalog and research entrypoints were added.
- Memory and harness evolution notes were added as cautious redesign inputs.

## Boundary

- Official references remain separate from:
  - active platform code
  - archived LoopMart product workspace
- Secondary references are discovery-only and are not treated as authority.

## Follow-up

- use the benchmark framework to test which external runtime patterns are
  actually better than the current platform
- redesign memory, commands, agents, and harnesses only after explicit
  benchmark-backed decisions
