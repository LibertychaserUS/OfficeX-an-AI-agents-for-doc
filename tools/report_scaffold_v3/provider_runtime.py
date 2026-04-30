from __future__ import annotations

from pathlib import Path
from typing import get_args

from .manifest_loader import load_provider_catalog
from .models import (
    OfficeXCompiledPromptBundle,
    OfficeXProviderRequestEnvelope,
    OfficeXProviderPromptBinding,
    ProviderCatalogEntryManifest,
    ProviderCatalogManifest,
    ProviderModelCapabilityManifest,
    ProviderResponseContractKind,
)
from .paths import DEFAULT_PROVIDER_CATALOG_MANIFEST
from .prompt_runtime import compile_officex_prompt_bundle, list_officex_roles
from .runtime_common import sanitize_runtime_identifier
from .task_runtime import load_task_packet


def _derive_required_config_fields(config_fields: list[str]) -> list[str]:
    return [field_name for field_name in config_fields if not field_name.endswith("_optional")]


def parse_provider_config_field_assignments(
    assignments: list[str] | None,
) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in assignments or []:
        if "=" not in item:
            raise ValueError(
                f"Invalid config field assignment `{item}`. Expected `name=value`."
            )
        field_name, raw_value = item.split("=", 1)
        normalized_name = field_name.strip()
        normalized_value = raw_value.strip()
        if not normalized_name:
            raise ValueError(f"Invalid config field assignment `{item}`. Field name is empty.")
        if not normalized_value:
            raise ValueError(
                f"Invalid config field assignment `{item}`. Field value is empty."
            )
        if normalized_name in parsed:
            raise ValueError(f"Duplicate OfficeX config field `{normalized_name}`.")
        parsed[normalized_name] = normalized_value
    return parsed


def list_provider_entries(
    catalog_path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST,
) -> list[ProviderCatalogEntryManifest]:
    catalog = load_provider_catalog(catalog_path)
    return list(catalog.providers)


def list_provider_ids(catalog_path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST) -> list[str]:
    return [entry.provider_id for entry in list_provider_entries(catalog_path)]


def load_provider_catalog_manifest(
    catalog_path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST,
) -> ProviderCatalogManifest:
    return load_provider_catalog(catalog_path)


def get_provider_entry(
    provider_id: str,
    *,
    catalog_path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST,
) -> ProviderCatalogEntryManifest:
    catalog = load_provider_catalog(catalog_path)
    for entry in catalog.providers:
        if entry.provider_id == provider_id:
            return entry
    raise ValueError(f"Unknown OfficeX provider `{provider_id}`.")


def resolve_provider_model(
    provider_id: str,
    *,
    model_id: str | None = None,
    catalog_path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST,
) -> ProviderModelCapabilityManifest:
    entry = get_provider_entry(provider_id, catalog_path=catalog_path)
    selected_model_id = model_id or entry.default_model_id
    for model in entry.models:
        if model.model_id == selected_model_id:
            return model
    available = ", ".join(model.model_id for model in entry.models)
    raise ValueError(
        f"Unknown model `{selected_model_id}` for OfficeX provider `{provider_id}`. "
        f"Available models: {available}"
    )


def _resolve_provider_context(
    provider_id: str,
    *,
    role: str,
    model_id: str | None,
    include_cognition: bool,
    catalog_path: Path,
) -> tuple[
    ProviderCatalogEntryManifest,
    ProviderModelCapabilityManifest,
    OfficeXCompiledPromptBundle,
    list[str],
]:
    if role not in list_officex_roles():
        raise ValueError(f"Unknown OfficeX role prompt: `{role}`.")

    entry = get_provider_entry(provider_id, catalog_path=catalog_path)
    model = resolve_provider_model(
        provider_id,
        model_id=model_id,
        catalog_path=catalog_path,
    )
    prompt_bundle = compile_officex_prompt_bundle(
        role,
        include_cognition=include_cognition,
    )
    notes = list(entry.notes)
    if model.risk_notes:
        notes.extend(model.risk_notes)
    return entry, model, prompt_bundle, notes


def build_provider_prompt_binding(
    provider_id: str,
    *,
    role: str,
    model_id: str | None = None,
    include_cognition: bool = True,
    catalog_path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST,
) -> OfficeXProviderPromptBinding:
    entry, model, prompt_bundle, notes = _resolve_provider_context(
        provider_id,
        role=role,
        model_id=model_id,
        include_cognition=include_cognition,
        catalog_path=catalog_path,
    )

    return OfficeXProviderPromptBinding(
        provider_id=entry.provider_id,
        provider_display_name=entry.display_name,
        adapter_kind=entry.adapter_kind,
        status=entry.status,
        auth_scheme=entry.auth_scheme,
        model_id=model.model_id,
        role=role,
        include_cognition=include_cognition,
        supports_structured_output=model.supports_structured_output,
        supports_tool_calls=model.supports_tool_calls,
        supports_image_generation=model.supports_image_generation,
        supports_long_context=model.supports_long_context,
        latency_class=model.latency_class,
        config_fields=entry.config_fields,
        notes=notes,
        prompt_manifest=prompt_bundle.prompt_manifest,
        resolved_rule_refs=prompt_bundle.resolved_rule_refs,
        compiled_prompt_debug=prompt_bundle.compiled_prompt_debug,
        prompt_trace_record=prompt_bundle.prompt_trace_record,
        prompt=prompt_bundle.compiled_prompt_debug,
    )


def build_provider_request_envelope(
    provider_id: str,
    *,
    role: str,
    model_id: str | None = None,
    include_cognition: bool = True,
    task_packet_path: Path | None = None,
    run_id: str | None = None,
    sandbox_root: Path,
    config_field_assignments: list[str] | None = None,
    response_contract_kind: ProviderResponseContractKind = "plan_object",
    catalog_path: Path = DEFAULT_PROVIDER_CATALOG_MANIFEST,
) -> OfficeXProviderRequestEnvelope:
    allowed_contract_kinds = set(get_args(ProviderResponseContractKind))
    if response_contract_kind not in allowed_contract_kinds:
        raise ValueError(
            "Unknown OfficeX response contract kind "
            f"`{response_contract_kind}`."
        )

    binding = build_provider_prompt_binding(
        provider_id,
        role=role,
        model_id=model_id,
        include_cognition=include_cognition,
        catalog_path=catalog_path,
    )
    task_packet = load_task_packet(
        task_packet_path=task_packet_path,
        run_id=run_id,
        sandbox_root=sandbox_root,
    )
    parsed_config = parse_provider_config_field_assignments(config_field_assignments)
    allowed_fields = set(binding.config_fields)
    unknown_fields = [field_name for field_name in parsed_config if field_name not in allowed_fields]
    if unknown_fields:
        raise ValueError(
            "Unknown OfficeX config field(s) for provider "
            f"`{provider_id}`: {', '.join(unknown_fields)}."
        )

    required_config_fields = _derive_required_config_fields(binding.config_fields)
    envelope_id = sanitize_runtime_identifier(
        f"{task_packet.task_packet_id}-{binding.provider_id}-{binding.role}-request",
        fallback="officex-provider-request",
    )
    return OfficeXProviderRequestEnvelope(
        envelope_id=envelope_id,
        provider_id=binding.provider_id,
        model_id=binding.model_id,
        adapter_kind=binding.adapter_kind,
        dispatch_mode="dry_run",
        role=binding.role,
        include_cognition=binding.include_cognition,
        task_packet_id=task_packet.task_packet_id,
        goal=task_packet.goal,
        task_family=task_packet.task_family,
        approval_mode=task_packet.approval_mode,
        system_prompt=binding.prompt,
        prompt_manifest=binding.prompt_manifest,
        resolved_rule_refs=binding.resolved_rule_refs,
        compiled_prompt_debug=binding.compiled_prompt_debug,
        prompt_trace_record=binding.prompt_trace_record,
        input_artifacts=task_packet.input_artifacts,
        constraints=task_packet.constraints,
        acceptance_gates=task_packet.acceptance_gates,
        expected_outputs=task_packet.expected_outputs,
        required_config_fields=required_config_fields,
        provided_config_fields=list(parsed_config.keys()),
        response_contract_kind=response_contract_kind,
        supports_structured_output=binding.supports_structured_output,
        supports_tool_calls=binding.supports_tool_calls,
        supports_image_generation=binding.supports_image_generation,
        supports_long_context=binding.supports_long_context,
        latency_class=binding.latency_class,
    )
