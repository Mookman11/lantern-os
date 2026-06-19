"""Regression tests for UnifiedAgentConnector._parse_sse framing (issue #628).

The Σ₀ coder rebuild surfaced that _parse_sse only accepted SSE "data:"-prefixed
lines, so Ollama's bare-JSONL stream yielded zero tokens. The fix must parse BOTH
framings without regressing cloud SSE providers. These tests feed synthetic byte
streams through the real _parse_sse via a fake urlopen — no network, no live model.
"""

import io
import urllib.request

from src.unified_agent_connector import UnifiedAgentConnector


class _FakeResp:
    """Minimal context-manager response that streams given bytes in chunks."""
    def __init__(self, body: bytes):
        self._buf = io.BytesIO(body)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, n=-1):
        return self._buf.read(n)


def _drain(connector, body: bytes, extract_fn):
    """Run _parse_sse over a synthetic response body; return the joined tokens."""
    gen = connector._parse_sse("http://x", b"{}", 5, extract_fn, {})
    return "".join(list(gen))


def _connector():
    return UnifiedAgentConnector()


def test_ollama_jsonl_stream_yields_tokens(monkeypatch):
    """Ollama streams bare JSONL (no 'data:' prefix) — the original bug."""
    body = (
        b'{"message":{"content":"def "}}\n'
        b'{"message":{"content":"f():"}}\n'
        b'{"done":true}\n'
    )
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=0: _FakeResp(body))
    extract = lambda d: d.get("message", {}).get("content", "") or d.get("response", "")
    assert _drain(_connector(), body, extract) == "def f():"


def test_openai_sse_stream_still_parses(monkeypatch):
    """Cloud SSE ('data:' prefixed) must keep working — regression guard."""
    body = (
        b'data: {"choices":[{"delta":{"content":"Hi"}}]}\n'
        b'data: {"choices":[{"delta":{"content":" there"}}]}\n'
        b'data: [DONE]\n'
    )
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=0: _FakeResp(body))
    extract = lambda d: d.get("choices", [{}])[0].get("delta", {}).get("content", "")
    assert _drain(_connector(), body, extract) == "Hi there"


def test_sse_control_lines_are_skipped(monkeypatch):
    """SSE 'event:' and comment ':' lines are not JSON and must be ignored, not crash."""
    body = (
        b': keep-alive\n'
        b'event: message\n'
        b'data: {"choices":[{"delta":{"content":"ok"}}]}\n'
    )
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=0: _FakeResp(body))
    extract = lambda d: d.get("choices", [{}])[0].get("delta", {}).get("content", "")
    assert _drain(_connector(), body, extract) == "ok"


def test_anthropic_content_block_delta_parses(monkeypatch):
    body = (
        b'data: {"type":"content_block_delta","delta":{"text":"X"}}\n'
        b'data: {"type":"message_stop"}\n'
    )
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=0: _FakeResp(body))
    extract = lambda d: d.get("delta", {}).get("text", "") if d.get("type") == "content_block_delta" else ""
    assert _drain(_connector(), body, extract) == "X"
