"""Provider adapter layer: dispatch request envelopes to live providers.

This module translates OfficeXProviderRequestEnvelope into actual API
calls.  It is provider-neutral at the interface level — the adapter_kind
field in the envelope selects the concrete dispatch path.

Security:
- API keys are NEVER read from files or embedded in code
- Keys are resolved from environment variables at dispatch time
- The adapter refuses to dispatch if the key is missing
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Literal

from .models import OfficeXProviderRequestEnvelope

logger = logging.getLogger(__name__)

PROVIDER_API_KEY_ENV = "OFFICEX_PROVIDER_API_KEY"
PROVIDER_BASE_URL_ENV = "OFFICEX_PROVIDER_BASE_URL"


@dataclass(frozen=True)
class ProviderDispatchResult:
    """Result of a live provider dispatch."""
    envelope_id: str
    provider_id: str
    model_id: str
    status: Literal["success", "error", "no_credentials"]
    response_text: str = ""
    usage: dict | None = None
    error_message: str = ""


def _resolve_api_key(envelope: OfficeXProviderRequestEnvelope) -> str | None:
    """Resolve API key from environment. Never from files."""
    key = os.environ.get(PROVIDER_API_KEY_ENV)
    if key:
        return key
    # Check provider-specific env var as fallback
    provider_key_env = f"OFFICEX_{envelope.provider_id.upper()}_API_KEY"
    return os.environ.get(provider_key_env)


def _resolve_base_url(envelope: OfficeXProviderRequestEnvelope) -> str | None:
    """Resolve base URL from environment or envelope config."""
    url = os.environ.get(PROVIDER_BASE_URL_ENV)
    if url:
        return url
    provider_url_env = f"OFFICEX_{envelope.provider_id.upper()}_BASE_URL"
    return os.environ.get(provider_url_env)


def _dispatch_openai_compatible(
    envelope: OfficeXProviderRequestEnvelope,
    *,
    api_key: str,
    base_url: str | None = None,
    max_retries: int = 2,
    retry_delay: float = 2.0,
) -> ProviderDispatchResult:
    """Dispatch via OpenAI-compatible chat completions API with retry."""
    from openai import OpenAI

    client_kwargs: dict = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)

    messages = [
        {"role": "system", "content": envelope.system_prompt},
        {"role": "user", "content": envelope.goal},
    ]

    logger.debug(
        "Dispatching to %s model=%s via %s",
        envelope.provider_id,
        envelope.model_id,
        base_url or "default",
    )

    last_error = ""
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=envelope.model_id,
                messages=messages,
                temperature=0.3,
            )
            choice = response.choices[0]
            usage_dict = None
            if response.usage:
                usage_dict = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return ProviderDispatchResult(
                envelope_id=envelope.envelope_id,
                provider_id=envelope.provider_id,
                model_id=envelope.model_id,
                status="success",
                response_text=choice.message.content or "",
                usage=usage_dict,
            )
        except Exception as exc:
            last_error = str(exc)
            if attempt < max_retries:
                logger.debug("Attempt %d failed (%s), retrying in %.1fs", attempt + 1, last_error, retry_delay)
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error("Provider dispatch failed after %d attempts: %s", max_retries + 1, last_error)

    return ProviderDispatchResult(
        envelope_id=envelope.envelope_id,
        provider_id=envelope.provider_id,
        model_id=envelope.model_id,
        status="error",
        error_message=last_error,
    )


def dispatch_envelope(
    envelope: OfficeXProviderRequestEnvelope,
) -> ProviderDispatchResult:
    """Dispatch a request envelope to its target provider.

    Resolves credentials from environment variables, selects the
    appropriate adapter based on adapter_kind, and returns the result.
    """
    api_key = _resolve_api_key(envelope)
    if not api_key:
        return ProviderDispatchResult(
            envelope_id=envelope.envelope_id,
            provider_id=envelope.provider_id,
            model_id=envelope.model_id,
            status="no_credentials",
            error_message=(
                f"No API key found. Set {PROVIDER_API_KEY_ENV} or "
                f"OFFICEX_{envelope.provider_id.upper()}_API_KEY."
            ),
        )

    base_url = _resolve_base_url(envelope)

    adapter_kind = envelope.adapter_kind
    if adapter_kind in {"openai_compatible_chat", "openai_compatible_local"}:
        return _dispatch_openai_compatible(
            envelope, api_key=api_key, base_url=base_url,
        )
    if adapter_kind == "anthropic_chat":
        # Anthropic uses the same OpenAI-compatible path when accessed
        # through compatible proxies; native Anthropic SDK can be added later
        return _dispatch_openai_compatible(
            envelope, api_key=api_key, base_url=base_url,
        )

    return ProviderDispatchResult(
        envelope_id=envelope.envelope_id,
        provider_id=envelope.provider_id,
        model_id=envelope.model_id,
        status="error",
        error_message=f"Unsupported adapter kind: {adapter_kind}",
    )
