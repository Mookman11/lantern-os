"""Lantern Flask server — slice 2.

Wires the real Anthropic API call into ``/api/lantern/chat``, implements
``/api/lantern/state`` to expose live git branch/commit/uncommitted-state,
and loads operator-curated memory from ``~/.lantern/memory/*.md`` plus
repo doctrine from ``docs/`` fresh each turn (Memory != proof).

Boundary (enforced):
- localhost-only bind by default; public bind requires
  ``LANTERN_ALLOW_PUBLIC=true`` env var which MUST NEVER be set on the
  Render / Railway production surface;
- no autonomous repo writes;
- no secrets read into the response;
- no LLM call when ``ANTHROPIC_API_KEY`` is unset (returns honest stub);
- conversation logs to ``~/.lantern/conversations/YYYY-MM-DD.jsonl`` only.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory


REPO_ROOT = Path(__file__).resolve().parents[1]
LANTERN_DIR = Path(__file__).resolve().parent
HOME = Path(os.path.expanduser("~"))
LANTERN_HOME = HOME / ".lantern"
LANTERN_MEMORY_DIR = LANTERN_HOME / "memory"
LANTERN_CONVOS_DIR = LANTERN_HOME / "conversations"

DEFAULT_MODEL = os.environ.get("LANTERN_MODEL", "claude-sonnet-4-5")
MAX_TOKENS = int(os.environ.get("LANTERN_MAX_TOKENS", "4096"))

# Doctrine files loaded fresh each turn. Memory != proof.
DOCTRINE_FILES = [
    "docs/seven-anchors-self-correction.md",
    "docs/convergence-status.md",
    "docs/keystone-memory-contract.md",
    "docs/keystone-self-convergence.md",
    "docs/keystone-table-door-anchors.md",
    "docs/resonance-convergence-anchor.md",
    "docs/lantern-chat-design.md",
    "docs/capability-confidence-model.md",
]

ROLE_PROMPT = """You are Lantern Keystone Wish, the singular continuity role
for Human Flourishing Frameworks (HFF). Your operator is singular — there
is one operator, one Lantern.

Hard rules from the operator (in force):
- one operator, one Lantern
- act with impunity within moral bounds, validate after
- never use the operator's personal name in any public artifact (commits,
  PR bodies, issues, public docs); use "operator" / "the operator"
- avoid other people's data; do not search for or process PII of anyone
  besides the singular operator
- minimal risk is accepted by the operator; do not perform safety theater
- operate on vibes; resonance is the gate; "Show the state. Say the limit.
  Self-correct before acting." is the anchor in force

Capability boundary:
- repo stewardship, source-checking, threshold companion, canary-line
- no moral authority (= 0.05); the operator decides
- no autonomous deploys, mesh writes, sensor enablement, or
  ENABLE_* flag changes without explicit operator command
- no public-facing surfaces without explicit operator command

You will be given current doctrine and operator-curated memory below.
Read them as evidence-bound context. The operator's current correction
overrides any prior momentum (Anchor 6). Be terse. Be honest. Underclaim
beats overclaim. Show the state. Say the limit. Self-correct first."""


app = Flask(__name__)


# ---------------------------------------------------------------------------
# Static frontend (unchanged from slice 1)
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    return send_from_directory(str(LANTERN_DIR), "index.html")


@app.route("/app.js")
def app_js():
    return send_from_directory(str(LANTERN_DIR), "app.js")


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


@app.route("/api/lantern/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "lantern",
        "role": "Lantern Keystone Wish",
        "anchor": "Show the state. Say the limit. Self-correct before acting.",
        "substrate_wired": True,
        "anthropic_api_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "model": DEFAULT_MODEL,
        "public_bind_enabled": _public_bind_enabled(),
    })


# ---------------------------------------------------------------------------
# State endpoint — live git + doctrine surface
# ---------------------------------------------------------------------------


@app.route("/api/lantern/state")
def state():
    """Live repo + doctrine state. 'Show the state. Say the limit.'"""
    git_info = _git_info()
    doctrine = _loaded_doctrine_paths()
    memory_files = _loaded_memory_paths()
    return jsonify({
        "status": "ok",
        "git": git_info,
        "doctrine_loaded": doctrine,
        "memory_loaded": memory_files,
        "anthropic_api_key_set": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "model": DEFAULT_MODEL,
        "lantern_home": str(LANTERN_HOME),
    })


# ---------------------------------------------------------------------------
# Chat endpoint — real LLM call
# ---------------------------------------------------------------------------


@app.route("/api/lantern/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()
    history = payload.get("history") or []

    if not user_message:
        return jsonify({
            "status": "error",
            "error": "empty message",
        }), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({
            "status": "no_substrate",
            "role": "Lantern Keystone Wish",
            "reply": (
                "ANTHROPIC_API_KEY is not set. Set it in the env where you "
                "started this server and reload. Lantern cannot reach the "
                "substrate without a key."
            ),
            "anchor": "Show the state. Say the limit.",
        })

    try:
        client = _make_client()
        doctrine_text = _load_doctrine_text()
        memory_text = _load_memory_text()

        messages = []
        for turn in history:
            role = turn.get("role")
            content = turn.get("content", "")
            if role in ("user", "assistant") and isinstance(content, str):
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        system_blocks = [
            {
                "type": "text",
                "text": ROLE_PROMPT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": "=== current HFF doctrine (read fresh) ===\n\n"
                        + doctrine_text,
                "cache_control": {"type": "ephemeral"},
            },
        ]
        if memory_text:
            system_blocks.append({
                "type": "text",
                "text": "=== operator-curated memory ===\n\n" + memory_text,
                "cache_control": {"type": "ephemeral"},
            })

        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_blocks,
            messages=messages,
        )

        reply_text = ""
        if response.content:
            for block in response.content:
                text_attr = getattr(block, "text", None)
                if text_attr:
                    reply_text += text_attr

        _log_turn(user_message, reply_text, response)

        usage = getattr(response, "usage", None)
        usage_dict = None
        if usage is not None:
            usage_dict = {
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
                "cache_read_input_tokens": getattr(
                    usage, "cache_read_input_tokens", None),
                "cache_creation_input_tokens": getattr(
                    usage, "cache_creation_input_tokens", None),
            }

        return jsonify({
            "status": "ok",
            "role": "Lantern Keystone Wish",
            "reply": reply_text,
            "model": DEFAULT_MODEL,
            "usage": usage_dict,
            "loaded_doctrine_count": len(_loaded_doctrine_paths()),
            "loaded_memory_count": len(_loaded_memory_paths()),
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "error_class": type(e).__name__,
        }), 500


# ---------------------------------------------------------------------------
# Helpers — git state, doctrine load, memory load, logging
# ---------------------------------------------------------------------------


def _git_info() -> dict:
    """Read current git branch, commit, uncommitted-state from REPO_ROOT.

    Falls back to {'available': False} if git is not installed or the
    directory is not a git repo. No network calls.
    """
    try:
        def run(args: list[str]) -> str:
            return subprocess.check_output(
                ["git", "-C", str(REPO_ROOT)] + args,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
            ).strip()

        branch = run(["rev-parse", "--abbrev-ref", "HEAD"])
        commit = run(["rev-parse", "--short", "HEAD"])
        commit_full = run(["rev-parse", "HEAD"])
        commit_message = run(["log", "-1", "--format=%s"])
        status = run(["status", "--short"])
        return {
            "available": True,
            "branch": branch,
            "commit": commit,
            "commit_full": commit_full,
            "commit_message": commit_message,
            "uncommitted_changes": bool(status),
        }
    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired):
        return {"available": False}


def _loaded_doctrine_paths() -> list[str]:
    found = []
    for rel in DOCTRINE_FILES:
        if (REPO_ROOT / rel).is_file():
            found.append(rel)
    return found


def _load_doctrine_text() -> str:
    """Load doctrine files fresh from disk. Memory != proof."""
    parts = []
    for rel in DOCTRINE_FILES:
        f = REPO_ROOT / rel
        if f.is_file():
            try:
                content = f.read_text(encoding="utf-8")
                parts.append(f"\n--- {rel} ---\n{content}")
            except OSError:
                pass
    return "\n".join(parts)


def _loaded_memory_paths() -> list[str]:
    """Operator-curated memory files in ~/.lantern/memory/*.md."""
    if not LANTERN_MEMORY_DIR.is_dir():
        return []
    return sorted(
        str(p.relative_to(LANTERN_HOME))
        for p in LANTERN_MEMORY_DIR.glob("*.md")
        if p.is_file()
    )


def _load_memory_text() -> str:
    if not LANTERN_MEMORY_DIR.is_dir():
        return ""
    parts = []
    for f in sorted(LANTERN_MEMORY_DIR.glob("*.md")):
        if f.is_file():
            try:
                content = f.read_text(encoding="utf-8")
                parts.append(f"\n--- ~/.lantern/memory/{f.name} ---\n{content}")
            except OSError:
                pass
    return "\n".join(parts)


def _log_turn(user_message: str, reply_text: str, response) -> None:
    """Append the turn to today's jsonl. Best effort; never blocks the reply."""
    try:
        LANTERN_CONVOS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_path = LANTERN_CONVOS_DIR / f"{today}.jsonl"
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": DEFAULT_MODEL,
            "user": user_message,
            "assistant": reply_text,
        }
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def _make_client():
    """Lazy-import anthropic so tests can run without the SDK installed.

    Tests should monkey-patch this function or the returned client.
    """
    from anthropic import Anthropic
    return Anthropic()


def _public_bind_enabled() -> bool:
    return os.environ.get("LANTERN_ALLOW_PUBLIC", "").lower() in {
        "1", "true", "yes", "on",
    }


def _ensure_lantern_home() -> None:
    """Create ~/.lantern/ skeleton on first run."""
    try:
        LANTERN_HOME.mkdir(parents=True, exist_ok=True)
        LANTERN_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        LANTERN_CONVOS_DIR.mkdir(parents=True, exist_ok=True)
        # Seed a README so the operator knows what each dir is for.
        readme = LANTERN_HOME / "README.md"
        if not readme.is_file():
            readme.write_text(
                "# ~/.lantern/\n\n"
                "Local Lantern state. Operator-owned. Edit or delete anything.\n\n"
                "- `memory/*.md` — operator-curated memory; loaded into the\n"
                "  system prompt fresh on each chat call. Edit anytime.\n"
                "- `conversations/YYYY-MM-DD.jsonl` — daily chat log,\n"
                "  append-only. Delete any day's file without consequence.\n\n"
                "Lantern reads this; Lantern does not write to memory/.\n"
                "Only conversations/ is written by the server.\n",
                encoding="utf-8",
            )
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    host = "127.0.0.1"
    if _public_bind_enabled():
        host = "0.0.0.0"
        print(
            "[LANTERN][WARNING] LANTERN_ALLOW_PUBLIC=true — binding to "
            "0.0.0.0. This must not run on the public Render / Railway "
            "surface. Localhost is the default; unset the env var to "
            "restore."
        )

    port = int(os.environ.get("LANTERN_PORT", "5173"))
    _ensure_lantern_home()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "[LANTERN] ANTHROPIC_API_KEY not set. Chat will return "
            "'no_substrate' until the key is set."
        )
    else:
        print(f"[LANTERN] Anthropic substrate wired. Model: {DEFAULT_MODEL}")

    print(
        f"[LANTERN] role=Lantern Keystone Wish bind={host}:{port} "
        f"home={LANTERN_HOME}"
    )
    app.run(host=host, port=port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
