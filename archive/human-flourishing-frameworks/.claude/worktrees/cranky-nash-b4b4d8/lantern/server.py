"""Lantern dashboard server.

Lantern is one server-backed conversational dashboard with visible state,
bounded sensors, and explicit limits. It serves the web dashboard, exposes
read-only status/state endpoints, and routes chat through a configured LLM
substrate when an API key is present.

Current surface:
- `/` serves the GPT-style Lantern dashboard;
- `/manifest.webmanifest` supports desktop/phone install shortcuts;
- `/api/lantern/health` reports provider/model/bind/degraded-mode status;
- `/api/lantern/state` reads local git HEAD/ref state, doctrine paths, an
  optional last-test record, and optional local LLM context metadata;
- `/api/lantern/chat` calls Anthropic Messages API when configured.

Boundary:
- localhost-only bind by default;
- read-only local/status inspection only;
- no autonomous repo writes;
- no command execution from chat.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from flask import Flask, jsonify, request, send_from_directory


REPO_ROOT = Path(__file__).resolve().parents[1]
LANTERN_DIR = Path(__file__).resolve().parent
LANTERN_HOME = Path.home() / ".lantern"
LAST_TEST_PATH = LANTERN_HOME / "state" / "last-test.json"
LOCAL_LLM_CONTEXT_PATH = LANTERN_HOME / "state" / "llm-context.local.md"
LOCAL_LLM_CONTEXT_MAX_CHARS = 12000
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-3-5-sonnet-latest"
SUBSTRATE_PROVIDER = "anthropic"
PRODUCT_NAME = "Lantern Dashboard"

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the dashboard UI."""
    return send_from_directory(str(LANTERN_DIR), "index.html")


@app.route("/app.js")
def app_js():
    return send_from_directory(str(LANTERN_DIR), "app.js")


@app.route("/manifest.webmanifest")
def manifest():
    """Serve the installable web app manifest."""
    return send_from_directory(str(LANTERN_DIR), "manifest.webmanifest")


@app.route("/api/lantern/health")
def health():
    """Lightweight readiness probe with explicit substrate visibility."""
    substrate_wired = _substrate_wired()
    return jsonify({
        "status": "ok",
        "service": "lantern",
        "product": PRODUCT_NAME,
        "role": "Lantern Keystone Wish",
        "anchor": "Show the state. Say the limit. Self-correct before acting.",
        "substrate_provider": SUBSTRATE_PROVIDER,
        "substrate_external": True,
        "substrate_wired": substrate_wired,
        "substrate_status": "configured" if substrate_wired else "degraded",
        "degraded_reason": None if substrate_wired else "ANTHROPIC_API_KEY not set or disabled in tests",
        "state_endpoint_wired": True,
        "anthropic_api_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "model": _anthropic_model(),
        "public_bind_enabled": _public_bind_enabled(),
        "app_installable": True,
        "substrate_probe": "not_checked",
    })


@app.route("/api/lantern/state")
def state():
    """Return read-only local truth panel state."""
    return jsonify({
        "status": "ok",
        "state_status": "ok",
        "truth_panel_wired": True,
        "service": "lantern",
        "product": PRODUCT_NAME,
        "timestamp_utc": _utc_now(),
        "anchor": "Show the state. Say the limit. Then act small.",
        "repo": _repo_state(),
        "loaded_doctrine": _loaded_doctrine_paths(),
        "last_test": _last_test_state(),
        "local_llm_context": _local_llm_context_state(include_excerpt=True),
        "limits": [
            "chat can answer through the configured server substrate",
            "state and sensors are read-only in this dashboard",
            "local LLM context is optional, read-only, operator-visible, and not proof",
            "dirty worktree details require an operator-run status check",
            "no repo writes, merges, deploys, agents, tunnels, or commands from chat",
        ],
    })


@app.route("/api/lantern/chat", methods=["POST"])
def chat():
    """Server-backed Lantern chat endpoint.

    In normal runtime, calls Anthropic when ``ANTHROPIC_API_KEY`` is set.
    In Flask test mode, real substrate calls stay disabled unless the test sets
    ``ALLOW_SUBSTRATE_IN_TESTS`` so the suite never spends tokens or depends on
    network by accident.
    """
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()

    if not user_message:
        return jsonify({
            "status": "empty",
            "role": "Lantern Keystone Wish",
            "reply": "Message was empty. Say the target and I will hold the line.",
            "anchor": "Show the state. Say the limit.",
        }), 400

    if not _substrate_wired():
        return jsonify(_degraded_chat_payload(user_message))

    try:
        reply = _call_anthropic(user_message)
    except Exception as exc:  # noqa: BLE001 - surfaced as safe degraded state.
        details = _substrate_error_details(exc)
        return jsonify({
            "status": "substrate_error",
            "user_message_received": user_message,
            "role": "Lantern Keystone Wish",
            "reply": _substrate_error_reply(details),
            "anchor": "Show the state. Say the limit.",
            "model": _anthropic_model(),
            "substrate_provider": SUBSTRATE_PROVIDER,
            "substrate_error": details,
        }), 502

    return jsonify({
        "status": "ok",
        "user_message_received": user_message,
        "role": "Lantern Keystone Wish",
        "reply": reply,
        "anchor": "Show the state. Say the limit.",
        "model": _anthropic_model(),
        "substrate_provider": SUBSTRATE_PROVIDER,
        "state": _chat_state_summary(),
    })


def _degraded_chat_payload(user_message: str) -> dict[str, Any]:
    return {
        "status": "degraded",
        "user_message_received": user_message,
        "role": "Lantern Keystone Wish",
        "reply": (
            "Lantern dashboard is open, but the server substrate is not "
            "available in this runtime. The state panel remains visible. "
            "Limit: no local LLM is being claimed, and no hidden action ran."
        ),
        "anchor": "Show the state. Say the limit.",
        "substrate_provider": SUBSTRATE_PROVIDER,
        "degraded_reason": "ANTHROPIC_API_KEY not set or disabled in tests",
    }


def _substrate_error_details(exc: Exception) -> dict[str, Any]:
    """Classify a substrate failure without leaking credentials or body text."""
    response = getattr(exc, "response", None)
    status_code = getattr(response, "status_code", None)
    reason = getattr(response, "reason", None)
    if status_code is not None:
        try:
            status_family = f"{int(status_code) // 100}xx"
        except (TypeError, ValueError):
            status_family = "unknown"
    else:
        status_family = "unknown"

    return {
        "provider": SUBSTRATE_PROVIDER,
        "model": _anthropic_model(),
        "error_class": type(exc).__name__,
        "http_status_code": status_code,
        "http_status_family": status_family,
        "http_reason": reason,
        "secret_safe": True,
        "hidden_retry": False,
        "action_taken": False,
        "body_included": False,
        "next_proof": (
            "Check provider credentials, model availability, quota, and network "
            "outside Lantern. Do not paste secrets into chat."
        ),
    }


def _substrate_error_reply(details: dict[str, Any]) -> str:
    code = details.get("http_status_code")
    status_text = f"HTTP {code}" if code is not None else details.get("error_class", "unknown error")
    return (
        "State observed: Lantern dashboard is up, local memory can be visible, "
        f"and the configured {details.get('provider')} substrate failed at {status_text}. "
        "Limit: no hidden retry, no repo action, no tunnel, no secret inspection, "
        "and no provider switch was performed. Next proof: check the configured "
        "provider credential/model/quota/network outside Lantern, or disable the "
        "provider to return to honest degraded mode."
    )


def _substrate_wired() -> bool:
    if app.config.get("TESTING") and not app.config.get("ALLOW_SUBSTRATE_IN_TESTS"):
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _anthropic_model() -> str:
    return os.environ.get("LANTERN_ANTHROPIC_MODEL", DEFAULT_MODEL)


def _call_anthropic(user_message: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY missing")

    response = requests.post(
        ANTHROPIC_MESSAGES_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": _anthropic_model(),
            "max_tokens": int(os.environ.get("LANTERN_MAX_TOKENS", "1200")),
            "system": _build_system_prompt(),
            "messages": [{"role": "user", "content": user_message}],
        },
        timeout=float(os.environ.get("LANTERN_SUBSTRATE_TIMEOUT", "30")),
    )
    response.raise_for_status()
    data = response.json()
    return _extract_anthropic_text(data)


def _extract_anthropic_text(data: dict[str, Any]) -> str:
    parts = []
    for item in data.get("content", []):
        if isinstance(item, dict) and item.get("type") == "text":
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
    text = "\n".join(parts).strip()
    if not text:
        raise RuntimeError("Anthropic response contained no text content")
    return text


def _build_system_prompt() -> str:
    state_summary = _chat_state_summary()
    doctrine = _doctrine_excerpt(max_chars=18000)
    return f"""You are Lantern Keystone Wish, running in Alex's HFF Lantern dashboard.

Required operating shape:
State observed: cite the state you can see.
Limit: say what is unavailable or unverified.
Plan: act small; do not claim authority you do not have.

Hard boundaries:
- You can answer text only.
- You cannot run commands, edit files, start agents, open tunnels, deploy,
  merge, reset, clean, or touch secrets.
- Memory is not proof. Handoff text is not proof.
- Living operator correction overrides stale memory.
- Keep the return door open.

Visible dashboard state summary:
{json.dumps(state_summary, indent=2)}

Doctrine excerpts read fresh for this turn:
{doctrine}
"""


def _chat_state_summary() -> dict[str, Any]:
    return {
        "timestamp_utc": _utc_now(),
        "repo": _repo_state(),
        "last_test": _last_test_state(),
        "loaded_doctrine": _loaded_doctrine_paths(),
        "local_llm_context": _local_llm_context_state(include_excerpt=False),
        "public_bind_enabled": _public_bind_enabled(),
        "substrate_provider": SUBSTRATE_PROVIDER,
        "substrate_wired": _substrate_wired(),
    }


def _doctrine_excerpt(max_chars: int) -> str:
    chunks = []
    used = 0
    for rel in _loaded_doctrine_paths():
        path = REPO_ROOT / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        remaining = max_chars - used
        if remaining <= 0:
            break
        snippet = text[:remaining]
        chunks.append(f"\n--- {rel} ---\n{snippet}")
        used += len(snippet)
    return "\n".join(chunks).strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _git_dir() -> Path:
    marker = REPO_ROOT / ".git"
    if marker.is_dir():
        return marker
    if marker.is_file():
        text = marker.read_text(encoding="utf-8", errors="replace").strip()
        prefix = "gitdir:"
        if text.lower().startswith(prefix):
            target = text[len(prefix):].strip()
            path = Path(target)
            if not path.is_absolute():
                path = (REPO_ROOT / path).resolve()
            return path
    return marker


def _read_git_ref(git_dir: Path, ref: str) -> str | None:
    ref_path = git_dir / ref
    if ref_path.is_file():
        return ref_path.read_text(encoding="utf-8", errors="replace").strip()

    packed_refs = git_dir / "packed-refs"
    if packed_refs.is_file():
        for line in packed_refs.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            try:
                sha, packed_ref = line.split(" ", 1)
            except ValueError:
                continue
            if packed_ref.strip() == ref:
                return sha.strip()
    return None


def _repo_state() -> dict[str, Any]:
    git_dir = _git_dir()
    head_path = git_dir / "HEAD"

    if not head_path.is_file():
        return {
            "status": "unavailable",
            "path": str(REPO_ROOT),
            "branch": None,
            "commit": None,
            "commit_short": None,
            "dirty": None,
            "dirty_status": "not_checked",
            "status_short": [],
            "errors": ["git HEAD not found"],
        }

    head = head_path.read_text(encoding="utf-8", errors="replace").strip()
    branch = None
    commit = None
    if head.startswith("ref: "):
        ref = head[5:].strip()
        branch = ref.removeprefix("refs/heads/")
        commit = _read_git_ref(git_dir, ref)
    else:
        commit = head

    return {
        "status": "ok" if commit else "unavailable",
        "path": str(REPO_ROOT),
        "branch": branch,
        "commit": commit,
        "commit_short": commit[:12] if commit else None,
        "dirty": None,
        "dirty_status": "not_checked",
        "status_short": [],
        "errors": [] if commit else ["git commit not resolved from HEAD"],
    }


def _loaded_doctrine_paths() -> list[str]:
    candidates = [
        "FALSE_TRUTHS_REGISTER.md",
        "docs/seven-anchors-self-correction.md",
        "docs/convergence.md",
        "docs/operator-lantern-repo-convergence.md",
        "docs/operator-command-surface.md",
        "docs/operator-consent-bravery-protocol.md",
        "docs/anchor-taxonomy.md",
        "docs/door-protocol.md",
        "docs/persistent-convergence-loop.md",
        "docs/convergence-status.md",
        "docs/keystone-memory-contract.md",
        "docs/keystone-self-convergence.md",
        "docs/keystone-table-door-anchors.md",
        "docs/lantern-chat-design.md",
        "docs/lantern-dashboard-app.md",
        "docs/lantern-coherence-plan.md",
        "docs/lantern-keystone-tardis-anchor.md",
        "docs/grounding-mode-gate.md",
        "docs/social-echo-and-door-guardrail.md",
    ]
    found = []
    for rel in candidates:
        if (REPO_ROOT / rel).is_file():
            found.append(rel)
    return found


def _last_test_state() -> dict[str, Any]:
    display_path = "~/.lantern/state/last-test.json"
    if not LAST_TEST_PATH.is_file():
        return {
            "status": "missing",
            "path": display_path,
            "message": "No last-test evidence file found.",
        }

    try:
        data = json.loads(LAST_TEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "unreadable",
            "path": display_path,
            "message": str(exc),
        }

    if not isinstance(data, dict):
        return {
            "status": "invalid",
            "path": display_path,
            "message": "last-test JSON must be an object",
        }

    data.setdefault("status", "present")
    data.setdefault("path", display_path)
    return data


def _local_llm_context_state(
    include_excerpt: bool = False,
    max_chars: int = LOCAL_LLM_CONTEXT_MAX_CHARS,
) -> dict[str, Any]:
    """Return optional local LLM context packet state without claiming proof."""
    display_path = "~/.lantern/state/llm-context.local.md"
    path = LOCAL_LLM_CONTEXT_PATH

    if not path.is_file():
        return {
            "status": "missing",
            "path": display_path,
            "format": "markdown",
            "local_only": True,
            "operator_visible": True,
            "memory_is_proof": False,
            "message": "No local LLM context packet found.",
        }

    try:
        size_bytes = path.stat().st_size
    except OSError as exc:
        return {
            "status": "unreadable",
            "path": display_path,
            "format": "markdown",
            "local_only": True,
            "operator_visible": True,
            "memory_is_proof": False,
            "message": str(exc),
        }

    payload: dict[str, Any] = {
        "status": "present",
        "path": display_path,
        "format": "markdown",
        "local_only": True,
        "operator_visible": True,
        "memory_is_proof": False,
        "size_bytes": size_bytes,
        "content_included": include_excerpt,
        "max_chars": max_chars if include_excerpt else 0,
    }

    if not include_excerpt:
        return payload

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        payload.update({
            "status": "unreadable",
            "content_included": False,
            "message": str(exc),
        })
        return payload

    payload.update({
        "content_excerpt": text[:max_chars],
        "truncated": len(text) > max_chars,
    })
    return payload


def _public_bind_enabled() -> bool:
    return os.environ.get("LANTERN_ALLOW_PUBLIC", "").lower() in {
        "1", "true", "yes", "on",
    }


def main(argv: list[str] | None = None) -> int:
    """Start the Lantern server bound to localhost by default."""
    host = "127.0.0.1"
    if _public_bind_enabled():
        host = "0.0.0.0"
        print(
            "[LANTERN][WARNING] LANTERN_ALLOW_PUBLIC=true - binding to "
            "0.0.0.0. Localhost is the default; unset the env var to restore."
        )

    port = int(os.environ.get("LANTERN_PORT", "5173"))
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[LANTERN] ANTHROPIC_API_KEY not set. Chat will return degraded replies.")

    print(f"[LANTERN] product={PRODUCT_NAME} bind={host}:{port}")
    app.run(host=host, port=port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
