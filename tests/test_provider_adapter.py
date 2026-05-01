"""Tests for provider adapter dispatch."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tools.report_scaffold_v3.provider_adapter import (
    ProviderDispatchResult,
    dispatch_envelope,
    PROVIDER_API_KEY_ENV,
)
from tools.report_scaffold_v3.models import (
    OfficeXPromptTraceRecord,
    OfficeXProviderRequestEnvelope,
)


def _make_envelope(**overrides) -> OfficeXProviderRequestEnvelope:
    defaults = dict(
        envelope_id="test-envelope",
        provider_id="openai",
        model_id="test-model",
        adapter_kind="openai_compatible_chat",
        dispatch_mode="live",
        role="orchestrator",
        include_cognition=True,
        task_packet_id="test-task",
        goal="Test goal",
        task_family="docx_mvp",
        approval_mode="ask_every_conflict",
        system_prompt="You are a test assistant.",
        prompt_manifest=[],
        resolved_rule_refs=[],
        compiled_prompt_debug="",
        prompt_trace_record=OfficeXPromptTraceRecord(
            role="orchestrator",
            compiled_prompt_sha256="abc123",
        ),
        input_artifacts=[],
        constraints=[],
        acceptance_gates=[],
        expected_outputs=[],
        required_config_fields=["api_key"],
        provided_config_fields=["api_key"],
        response_contract_kind="plan_object",
        supports_structured_output=True,
        supports_tool_calls=True,
        supports_image_generation=False,
        supports_long_context=True,
        latency_class="medium",
    )
    defaults.update(overrides)
    return OfficeXProviderRequestEnvelope(**defaults)


def test_dispatch_returns_no_credentials_when_key_missing(monkeypatch):
    monkeypatch.delenv(PROVIDER_API_KEY_ENV, raising=False)
    monkeypatch.delenv("OFFICEX_OPENAI_API_KEY", raising=False)
    envelope = _make_envelope()
    result = dispatch_envelope(envelope)
    assert result.status == "no_credentials"


def test_dispatch_returns_error_for_unsupported_adapter(monkeypatch):
    monkeypatch.setenv(PROVIDER_API_KEY_ENV, "test-key")
    envelope = _make_envelope(adapter_kind="unknown_adapter")
    result = dispatch_envelope(envelope)
    assert result.status == "error"
    assert "Unsupported adapter" in result.error_message


def test_dispatch_calls_openai_compatible_with_correct_params(monkeypatch):
    monkeypatch.setenv(PROVIDER_API_KEY_ENV, "test-key")
    monkeypatch.setenv("OFFICEX_PROVIDER_BASE_URL", "https://test.example.com/v1")

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30

    with patch("openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        MockOpenAI.return_value = mock_client

        envelope = _make_envelope()
        result = dispatch_envelope(envelope)

        MockOpenAI.assert_called_once_with(
            api_key="test-key",
            base_url="https://test.example.com/v1",
        )
        assert result.status == "success"
        assert result.response_text == "Test response"
        assert result.usage["total_tokens"] == 30


def test_dispatch_handles_api_error_gracefully(monkeypatch):
    monkeypatch.setenv(PROVIDER_API_KEY_ENV, "test-key")

    with patch("openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API rate limit")
        MockOpenAI.return_value = mock_client

        envelope = _make_envelope()
        result = dispatch_envelope(envelope)

        assert result.status == "error"
        assert "API rate limit" in result.error_message
