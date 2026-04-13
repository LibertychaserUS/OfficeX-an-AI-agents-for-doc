---
doc_id: provider_adapter_contract
layer: blueprint
authority: active
status: living
owner: platform_governance
machine_source_of_truth: false
---

# Provider Adapter Contract

## Purpose

This document defines how OfficeX integrates multiple AI providers while
keeping one stable runtime contract.

## Design Rule

OfficeX should target a provider-neutral runtime.

Models may differ, but:

- task packets
- patch contracts
- memory layering
- approval semantics
- audit rules

must remain stable above the provider layer.

## Provider Adapter Responsibilities

Each adapter should normalize:

- authentication
- model selection
- capability metadata
- structured output mode
- tool-calling behavior
- retry behavior
- timeout behavior
- token/context constraints
- rate-limit handling

## Capability Matrix

Each provider entry should expose at least:

- `provider_id`
- `model_id`
- `supports_structured_output`
- `supports_tool_calls`
- `supports_image_generation`
- `supports_long_context`
- `latency_class`
- `risk_notes`

## Runtime Contract

Above the provider layer, OfficeX should ask for:

- plan objects
- section drafts
- review findings
- asset-generation code
- patch proposals

The adapter should convert provider-specific responses into those common
objects.

## Cognition Injection Rule

Provider adapters should prepend the OfficeX cognition layer and the selected
role/domain prompt layers before dispatching a request.

External provider defaults must not become OfficeX runtime behavior by accident.

## Fallback Rule

Fallback may occur only when:

- the active model is unavailable
- the active model lacks a required capability
- rate limits or hard failures block the run

Fallback should be logged and should respect the current approval mode.

## Security Rule

Provider adapters should:

- keep credentials out of trace docs
- use local secure storage where possible
- avoid leaking full protected documents when narrower excerpts are enough
- record the provider/model used for a run

## Benchmark Rule

New providers or models should be benchmarked against:

- prompt compliance
- structured output quality
- truthfulness stability
- review usefulness
- latency and failure behavior

## MVP Rule

The first shipping implementation may expose only a small set of providers, but
the adapter interface should already assume future expansion.
