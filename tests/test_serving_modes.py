"""
Serving-mode + decode-param tests (PR #723 landing / issue #729).

Covers the issue's Definition of Done that is checkable without live providers:
  - FAST mode is the default (no OURO_NATIVE) and DEEP mode is opt-in.
  - FAST decode params are top_p=0.95 / frequency_penalty=0.5 (anti-token-loop).
  - The unified_agent_connector actually injects those params into each provider
    payload (Ollama uses repeat_penalty/repeat_last_n; OpenAI/Groq/Deepseek use
    frequency_penalty), and Anthropic is left unmodified (no frequency_penalty).
"""

import json
import os
import sys

import pytest

sys.path.insert(0, "src")

import serving_modes  # noqa: E402
import unified_agent_connector as uac  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_ouro_native(monkeypatch):
    monkeypatch.delenv("OURO_NATIVE", raising=False)
    yield


# ---- serving_modes unit behavior -------------------------------------------
def test_fast_mode_is_default():
    assert serving_modes.get_serving_mode().name == "fast"


@pytest.mark.parametrize("val", ["1", "true", "YES"])
def test_ouro_native_opts_into_deep(monkeypatch, val):
    monkeypatch.setenv("OURO_NATIVE", val)
    assert serving_modes.get_serving_mode().name == "deep"


def test_fast_decode_params_match_issue_729():
    dp = serving_modes.get_decode_params(serving_modes.FAST_MODE)
    assert dp["top_p"] == 0.95
    assert dp["frequency_penalty"] == 0.5
    # Ollama-specific anti-repetition knobs are present too.
    assert dp["repetition_penalty"] == 1.1
    assert dp["repeat_last_n"] == 64


def test_deep_decode_params_are_gentler():
    dp = serving_modes.get_decode_params(serving_modes.DEEP_MODE)
    assert dp["top_p"] == 0.98
    assert dp["frequency_penalty"] == 0.2


# ---- connector wiring: capture the payload each provider builds -------------
def _capture_payload(monkeypatch, provider, **env):
    """Call a connector _stream_<provider> and return the JSON body it would POST."""
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    captured = {}

    def fake_parse(self, url, payload, timeout, extract, headers):
        captured["body"] = json.loads(payload.decode())
        return iter(())

    monkeypatch.setattr(uac.UnifiedAgentConnector, "_parse_sse", fake_parse)
    conn = uac.UnifiedAgentConnector()
    cfg = type("Cfg", (), {})()
    cfg.model, cfg.api_key, cfg.base_url = "m", "k", None
    cfg.temperature, cfg.max_tokens, cfg.timeout = 0.7, 1024, 30
    list(getattr(conn, f"_stream_{provider}")(cfg, "sys", "hi", 0.2, 256))
    return captured["body"]


@pytest.mark.parametrize("provider", ["openai", "groq", "deepseek"])
def test_openai_compatible_providers_get_fast_decode_params(monkeypatch, provider):
    body = _capture_payload(monkeypatch, provider)
    assert body["top_p"] == 0.95
    assert body["frequency_penalty"] == 0.5


def test_ollama_gets_repeat_penalty_form(monkeypatch):
    body = _capture_payload(monkeypatch, "ollama")
    opts = body["options"]
    assert opts["top_p"] == 0.95
    assert opts["repeat_penalty"] == 1.1
    assert opts["repeat_last_n"] == 64
    # Ollama must NOT receive the OpenAI-style frequency_penalty key.
    assert "frequency_penalty" not in opts


def test_deep_mode_switches_connector_params(monkeypatch):
    body = _capture_payload(monkeypatch, "openai", OURO_NATIVE="1")
    assert body["top_p"] == 0.98
    assert body["frequency_penalty"] == 0.2


def test_anthropic_is_not_given_frequency_penalty(monkeypatch):
    # Anthropic's API has no frequency_penalty; the connector must not add one.
    body = _capture_payload(monkeypatch, "anthropic")
    assert "frequency_penalty" not in body
