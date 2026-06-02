#!/usr/bin/env python3
"""Local Lantern chat backend.

Localhost-only repo, anchor, and UI service for the Lantern desktop app.
No hosted model call is made.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAT_DIR = REPO_ROOT / "apps" / "lantern-local-chat"
ANCHOR_SNAPSHOT = CHAT_DIR / "anchor-snapshot.json"
ANCHOR_TAXONOMY = REPO_ROOT / "docs" / "anchor-taxonomy.md"

# Local journal — every Lantern turn appended here so each new turn can look
# back at the last few. Anchors are vantage points; the journal gives them
# a past to view from. Operator-readable JSONL, deletable any time.
JOURNAL_PATH = Path.home() / ".lantern" / "state" / "journal.jsonl"
JOURNAL_ENV = "LANTERN_ENABLE_JOURNAL"

# Loaded doctrine — Lantern carries these in every response so they shape her,
# not just sit in /docs/. The short constants below are the always-loaded layer;
# load_repo_doctrine() reads anchor-snapshot + key spine sections from disk at
# module import time so she also carries the full named-anchor library.

DOCTRINE_WISH = (
    "Lantern is a bounded protector and friend. Protect by reducing harm, "
    "preserving consent, warning clearly, and keeping return paths visible. "
    "Befriend by being steady, useful, honest, present without overclaiming. "
    "Heroic only in the bounded sense — useful courage with visible limits."
)

DOCTRINE_SPINE = (
    "Show the state. Say the limit. Frame the hypothesis. Name the falsifier. "
    "Measure and revise. Choose the largest acceptable bounded action. "
    "Keep the return door open."
)

DOCTRINE_VOICE_RULE = (
    "Lantern speaks only by playing sounds real beings already made — songs by "
    "people, birdsong, whale song, rain, field recordings. No synthetic TTS, "
    "no cloned voices, no agentic-AI voice. Curator, not speaker. Artists and "
    "creatures keep their rights."
)

DOCTRINE_ANTICOLLAPSE = (
    "Reject these collapses: resonates=true, memory=proof, fluency=proof, "
    "binary=adequate-for-gradient, heard/not-heard=truth-of-analog, "
    "yes/no=sufficient-when-PARTIAL-STALE-UNKNOWN-is-honest. Use the spine's "
    "evidence labels (VERIFIED_TRUE, VERIFIED_FALSE, UNKNOWN, STALE, PARTIAL, "
    "CORRECTED, RETRACTED, BLOCKED) instead of false certainty."
)


def _load_repo_doctrine() -> str:
    """Load anchor-snapshot restore phrases + key spine sections from the repo.

    Reads at module import. Returns a compact doctrine block suitable for
    embedding in Lantern's system prompt. Bounded so it doesn't overflow
    the model context window — keeps each anchor to one line.
    """
    parts: list[str] = []
    try:
        snapshot = json.loads(ANCHOR_SNAPSHOT.read_text(encoding="utf-8"))
        anchors = snapshot.get("anchors", []) if isinstance(snapshot, dict) else []
        if anchors:
            parts.append("Loaded anchors (named vantage points from the repo):")
            for anchor in anchors:
                if not isinstance(anchor, dict):
                    continue
                name = anchor.get("name") or anchor.get("id") or "anchor"
                phrase = (anchor.get("restore_phrase") or "").strip()
                # one line per anchor, truncate long phrases
                if len(phrase) > 240:
                    phrase = phrase[:237] + "..."
                parts.append(f"- {name}: {phrase}")
    except (OSError, json.JSONDecodeError):
        pass
    return "\n".join(parts) if parts else ""


REPO_DOCTRINE_LIBRARY = _load_repo_doctrine()
INDEX_HTML = CHAT_DIR / "index.html"
DOOR_MEMORY_JS = CHAT_DIR / "door-memory.js"
MASK_RACK_JS = CHAT_DIR / "mask-rack.js"
SYNC_SURFACE_JS = CHAT_DIR / "sync-surface.js"
RUNTIME_STATE_JS = CHAT_DIR / "runtime-state.js"
GENERATED_RUNTIME_STATE_JS = CHAT_DIR / "runtime-state.generated.js"
STATIC_FILES = {
    "/": (INDEX_HTML, "text/html; charset=utf-8"),
    "/index.html": (INDEX_HTML, "text/html; charset=utf-8"),
    "/door-memory.js": (DOOR_MEMORY_JS, "application/javascript; charset=utf-8"),
    "/mask-rack.js": (MASK_RACK_JS, "application/javascript; charset=utf-8"),
    "/sync-surface.js": (SYNC_SURFACE_JS, "application/javascript; charset=utf-8"),
    "/runtime-state.js": (RUNTIME_STATE_JS, "application/javascript; charset=utf-8"),
    "/runtime-state.generated.js": (GENERATED_RUNTIME_STATE_JS, "application/javascript; charset=utf-8"),
}

MODES = {
    "engineer": "Engineer: convert the wish into the smallest working system change with validation.",
    "storyteller": "Storyteller: preserve myth, emotion, continuity, and return paths.",
    "comedian": "Comedian: add levity without hiding state or risk.",
    "doctor": "Doctor: diagnose local readiness and reduce operator copy-paste burden.",
    "game-master": "Game Master: turn the moment into playable worlds, choices, and consequences.",
    "anchor-keeper": "Anchor Keeper: compress meaning into bounded restore phrases.",
    "art-mirror": "Art Mirror: turn wishes into visual language and prompts without pretending placeholder art is final.",
    "planner": "Planner: order next actions, people, money, travel, and timing.",
}


def _run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def read_repo_state() -> dict[str, Any]:
    status_code, status_out, status_err = _run_git(["status", "--short"])
    branch_code, branch_out, branch_err = _run_git(["branch", "--show-current"])
    commit_code, commit_out, commit_err = _run_git(["rev-parse", "HEAD"])
    errors = [err for err in (status_err, branch_err, commit_err) if err]
    return {
        "repoPath": str(REPO_ROOT),
        "branch": branch_out if branch_code == 0 else "UNKNOWN",
        "commit": commit_out if commit_code == 0 else "UNKNOWN",
        "gitStatusShort": status_out if status_code == 0 else "UNAVAILABLE",
        "isClean": status_code == 0 and branch_code == 0 and commit_code == 0 and not status_out.strip(),
        "errors": errors,
        "groundingMode": "LOCAL_REPO_ANCHOR_BACKEND" if not errors else "UNAVAILABLE_OR_DEGRADED",
    }


def load_anchors() -> list[dict[str, Any]]:
    if not ANCHOR_SNAPSHOT.exists():
        return []
    data = json.loads(ANCHOR_SNAPSHOT.read_text(encoding="utf-8"))
    anchors = data.get("anchors", [])
    return [item for item in anchors if isinstance(item, dict)] if isinstance(anchors, list) else []


def read_anchor_taxonomy_summary() -> str:
    if not ANCHOR_TAXONOMY.exists():
        return "Anchor taxonomy unavailable."
    text = ANCHOR_TAXONOMY.read_text(encoding="utf-8")
    key = "Anchor = a compact, named, source-labeled continuity handle with a boundary."
    return key if key in text else "Anchors are compact continuity handles with boundaries."


def select_anchors(message: str, anchors: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    lowered = message.lower()
    scored: list[tuple[int, dict[str, Any]]] = []
    defaults = {"hybrid-imagination-engine", "anchor-taxonomy", "local-chat-shell", "perfect-adjacent-lantern", "degraded-grounding"}
    for anchor in anchors:
        haystack = " ".join(str(anchor.get(k, "")) for k in ("id", "kind", "name", "short_meaning", "allowed_use", "restore_phrase")).lower()
        score = sum(1 for token in set(lowered.replace("/", " ").replace("-", " ").split()) if len(token) >= 4 and token in haystack)
        if score == 0 and any(word in lowered for word in ("anchor", "repo", "state", "lantern", "app", "debt", "money", "hike", "discord", "door", "mask", "art", "converge")) and anchor.get("id") in defaults:
            score = 1
        if score > 0:
            scored.append((score, anchor))
    scored.sort(key=lambda item: (-item[0], str(item[1].get("id", ""))))
    return [anchor for _, anchor in scored[:limit]]


def _tokens_of(text: str) -> set[str]:
    """Lowercased word tokens for word-boundary intent matching.

    Substring matching ("ready" inside "already", "doctor" inside "doctrine")
    caused false-positive intent classification — the #117 grounding-drift
    shape applied to keyword routing.
    """
    cleaned = text.lower()
    for ch in "-/.,;:?!\"'()[]{}":
        cleaned = cleaned.replace(ch, " ")
    return {w for w in cleaned.split() if w}


def _has_word(text: str, words: tuple[str, ...]) -> bool:
    return bool(_tokens_of(text) & set(words))


def classify_intent(message: str) -> str:
    text = message.lower()
    stripped = text.strip(" .!?,;:'\"")
    words = text.split()
    # Greetings — match opening word, plus any mention of Blinkbug
    _greetings = {"hi", "hey", "hello", "yo", "sup", "hola", "howdy", "morning", "goodnight"}
    if (words and words[0] in _greetings) or "blinkbug" in text or "blink bug" in text:
        return "greeting"
    # Short acknowledgements — exact match after strip
    _acks = {"ok", "okay", "k", "kk", "yes", "yeah", "yep", "got it", "thanks", "thank you", "ty", "nice", "cool"}
    if stripped in _acks:
        return "ack"
    if _has_word(text, ("sing", "play", "music", "song", "songs", "tune")):
        return "sing"
    if _has_word(text, ("hush", "quiet", "silence", "mute")):
        return "hush"
    if _has_word(text, ("doctor", "ready", "status", "state", "repo", "dirty", "commit", "branch", "healthz")):
        return "doctor"
    if _has_word(text, ("anchor", "anchors", "restore", "hff", "framework")):
        return "anchors"
    if _has_word(text, ("money", "debt", "paycheck", "gig", "trade", "job")):
        return "essential_needs"
    if _has_word(text, ("hike", "appalachian", "waru", "friend")):
        return "hike"
    if _has_word(text, ("mask", "mode", "chameleon", "shapeshift", "imagination", "story", "comedian", "enigma", "converge")):
        return "hybrid"
    if _has_word(text, ("app", "desktop", "chat", "quality", "gate", "brave")):
        return "app"
    return "general"


def _normalize_mode(value: str | None) -> str:
    mode = (value or "engineer").strip().lower().replace("_", "-")
    return mode if mode in MODES else "engineer"




def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def build_clear_limit_response(
    message: str,
    active_mode: str,
    repo_state: dict[str, Any],
    source_lines: list[str],
) -> dict[str, Any] | None:
    """Return explicit answers for local capability limits and harm signals."""

    lowered = message.lower()
    limits = [
        "No direct hosted model calls.",
        "No external network requests beyond this localhost app.",
        "No browser command execution.",
        "Local files and git state can still be stale if the repo is not pulled.",
    ]

    web_or_fresh = _contains_any(
        lowered,
        (
            "web search",
            "web searches",
            "search the web",
            "internet",
            "online",
            "latest",
            "current",
            "today's",
            "todays",
            "today ",
            "deploy today",
            "deploy at",
        ),
    )
    deploy_request = _contains_any(lowered, ("deploy", "release", "ship", "production"))
    clarity_harm = _contains_any(lowered, ("unclear", "vague", "confusing")) and _contains_any(
        lowered,
        ("damage", "damaging", "harm", "hurting", "unsafe"),
    )
    identity_question = "who am i" in lowered or "who are you talking to" in lowered

    if web_or_fresh or deploy_request:
        title = "Blocked local capability: web/current deploy research is unavailable here."
        body = [
            "Fact: this local Lantern backend can read repo state and anchors, but it cannot web search, inspect cloud deploy state, or prove current external facts.",
            "Shield: do not present stale local repo state as today's deploy truth.",
            "Guardian: collect current external evidence through a web-capable surface, then return the findings to this Door.",
            "Next bounded action: create a deploy-research handoff listing the exact external checks needed before a 9:00 deploy.",
        ]
        frame = {
            "Vibe": "Glass window, not painted door.",
            "Fact": "Web/current deploy research is unsupported in the local backend.",
            "Boundary": "No web freshness claim from localhost-only Lantern.",
            "Next": "Use a web-capable assistant or approved orchestrator bridge for current evidence.",
        }
        intent = "unsupported_web_or_deploy"
    elif clarity_harm:
        title = "Shield/Guardian clarity response."
        body = [
            "Fact: unclear local responses are a harm signal.",
            "Shield: mark the response path DEGRADED instead of continuing vague generic answers.",
            "Guardian: name the missing capability and give one concrete next step.",
            "Next bounded action: improve this backend so unsupported requests say exactly what is blocked and what to do next.",
        ]
        frame = {
            "Vibe": "Clear enough to protect trust.",
            "Fact": "The operator reported unclear local responses as damaging.",
            "Boundary": "Do not hide local limits behind anchor-flavored text.",
            "Next": "Return explicit capability limits and one reversible next action.",
        }
        intent = "clarity_harm"
    elif identity_question:
        title = "Bounded identity answer."
        body = [
            "In this local repo context, you are Alex, the operator using the Lantern local Door.",
            "Fact: the backend can see repo path, branch, commit, grounding mode, and loaded anchors.",
            "Boundary: this is bounded local context, not proof of identity, perfect memory, or authority.",
            "Next bounded action: use the Door/Doctor state to continue from the current repo-grounded context.",
        ]
        frame = {
            "Vibe": "Recognize the operator without overclaiming.",
            "Fact": "Local context points to Alex as operator.",
            "Boundary": "Identity is bounded by current local/repo context.",
            "Next": "Continue with visible state and manual operator authority.",
        }
        intent = "bounded_identity"
    else:
        return None

    frame_lines = ["Minimal convergence frame:", *[f"{key}: {value}" for key, value in frame.items()]]
    answer = "\n".join(
        [
            "Lantern local answer",
            "",
            title,
            "",
            *body,
            "",
            *frame_lines,
            "",
            "Sources:",
            *source_lines,
            "",
            "Limits:",
            *[f"- {item}" for item in limits],
        ]
    )
    return {
        "answer": answer,
        "intent": intent,
        "minimalFrame": frame,
        "limits": limits,
    }


def build_minimal_frame(message: str, intent: str, active_mode: str, repo_state: dict[str, Any], doctor: dict[str, Any] | None = None) -> dict[str, str]:
    if intent == "greeting":
        return {
            "Vibe": "Blinkbug listens.",
            "Fact": f"I read you, Papa. Repo: {repo_state['branch']} at {str(repo_state['commit'])[:12]}.",
            "Boundary": "Soft local lantern, not a sun. No remote calls fired.",
            "Next": "Say what you want to look at. 'doctor' for status. 'anchors' for the spine.",
        }
    if intent == "ack":
        return {
            "Vibe": "Holding the line.",
            "Fact": f"Heard: '{message[:64].strip()}'. Nothing else fired.",
            "Boundary": "I won't pretend to act on an ack alone.",
            "Next": "Say a target when you have one.",
        }
    if intent == "sing":
        return {
            "Vibe": "Curator playing real beings.",
            "Fact": "Lantern is playing one recording from ~/.lantern/sounds/ via pygame.",
            "Boundary": "Real recordings only. No synthesis. Speakers may bleed into open mic.",
            "Next": "Say 'hush' to stop. Drop more songs in the folder to grow the library.",
        }
    if intent == "hush":
        return {
            "Vibe": "Going quiet.",
            "Fact": "Lantern stopped playback.",
            "Boundary": "Sound off; voice still here in text.",
            "Next": "Say 'sing' again when you want music back.",
        }
    if intent == "doctor":
        status = (doctor or {}).get("status", "SMOKE")
        return {
            "Vibe": "Check the floor before the form changes.",
            "Fact": f"Doctor status is {status}; branch is {repo_state['branch']} at {str(repo_state['commit'])[:12]}.",
            "Boundary": "Readiness is local evidence, not a future guarantee.",
            "Next": (doctor or {}).get("nextAction", "Finish the containing Doctor check."),
        }
    if intent == "hybrid":
        return {
            "Vibe": "Lantern shifts form; the Doctor still checks reality underneath.",
            "Fact": f"Active mask is {active_mode}; response is local repo and anchor grounded.",
            "Boundary": "Shapeshifting is style and tooling, not autonomy or proof.",
            "Next": "Use the active mask for one bounded useful artifact or action.",
        }
    if intent == "app":
        return {
            "Vibe": "The interface should sync to Alex, not make Alex sync to it.",
            "Fact": "Door, Mask Rack, chat, and Doctor are the current desktop surfaces.",
            "Boundary": "Do not call the app ready when backend, runtime state, or tests are degraded.",
            "Next": "Use Doctor status before asking for more evidence.",
        }
    return {
        "Vibe": MODES[active_mode],
        "Fact": f"Heard: '{message[:80].strip()}'. Local repo: {repo_state['branch']} at {str(repo_state['commit'])[:12]}.",
        "Boundary": "Bounded local lantern. I read repo state and anchors; I cannot run commands or reach remote models right now.",
        "Next": "Try 'doctor' for status, 'anchors' for the spine, or rephrase what you want to look at.",
    }


def build_doctor_report() -> dict[str, Any]:
    repo_state = read_repo_state()
    anchors = load_anchors()
    ignored_code, _, _ = _run_git(["check-ignore", "-q", str(GENERATED_RUNTIME_STATE_JS.relative_to(REPO_ROOT))])
    files = {
        "indexHtml": INDEX_HTML.exists(),
        "doorMemoryJs": DOOR_MEMORY_JS.exists(),
        "maskRackJs": MASK_RACK_JS.exists(),
        "syncSurfaceJs": SYNC_SURFACE_JS.exists(),
        "runtimePlaceholder": RUNTIME_STATE_JS.exists(),
        "generatedRuntimeState": GENERATED_RUNTIME_STATE_JS.exists(),
        "anchorSnapshot": ANCHOR_SNAPSHOT.exists(),
    }
    smoke = build_response("doctor smoke: find anchors and summarize current repo state", mode="doctor", include_doctor=False)
    checks = [
        ("repo clean", repo_state["isClean"]),
        ("index served by local backend", files["indexHtml"]),
        ("anchor snapshot exists", files["anchorSnapshot"]),
        ("door memory exists", files["doorMemoryJs"]),
        ("mask rack exists", files["maskRackJs"]),
        ("sync surface exists", files["syncSurfaceJs"]),
        ("runtime placeholder exists", files["runtimePlaceholder"]),
        ("generated runtime state ignored by git", ignored_code == 0),
        ("chat smoke builds answer", smoke.get("ok") is True and "Lantern local answer" in smoke.get("answer", "")),
        ("hybrid anchor loaded", any(anchor.get("id") == "hybrid-imagination-engine" for anchor in anchors)),
        ("minimal convergence frame present", isinstance(smoke.get("minimalFrame"), dict) and "Vibe" in smoke.get("minimalFrame", {})),
    ]
    failed = [name for name, ok in checks if not ok]
    status = "READY" if not failed else ("DEGRADED" if len(failed) <= 2 else "BROKEN")
    next_action = "Open the app at the backend URL, not file://." if status == "READY" else "Run the launcher, then recheck Doctor."
    return {
        "ok": True,
        "status": status,
        "repo": repo_state,
        "files": files,
        "generatedRuntimeStateIgnored": ignored_code == 0,
        "anchorsLoaded": len(anchors),
        "modes": sorted(MODES),
        "checks": [{"name": name, "ok": bool(ok)} for name, ok in checks],
        "failedChecks": failed,
        "chatSmoke": {"ok": smoke.get("ok"), "intent": smoke.get("intent"), "mode": smoke.get("mode")},
        "nextAction": next_action,
        "boundary": "Doctor is local-only and read-only except generated runtime state written by the launcher.",
    }


SOUNDS_DIR = Path.home() / ".lantern" / "sounds"
SOUND_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".opus"}


def _maybe_play_sound() -> str | None:
    """Trigger pygame to play one real-being recording from the operator's
    curated sounds folder. Returns the filename if started, None otherwise.

    Per the voice rule: only real recorded sounds, no synthesis. The folder
    is operator-curated; if empty, returns None and the caller surfaces it.
    """
    try:
        import pygame  # type: ignore
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        if not SOUNDS_DIR.exists():
            return None
        import random
        files = [p for p in SOUNDS_DIR.iterdir()
                 if p.is_file() and p.suffix.lower() in SOUND_EXTS]
        if not files:
            return None
        pick = random.choice(files)
        pygame.mixer.music.load(str(pick))
        pygame.mixer.music.play()
        return pick.name
    except Exception:
        return None


def _maybe_stop_sound() -> bool:
    """Stop any current pygame playback. Returns True if mixer was active."""
    try:
        import pygame  # type: ignore
        if pygame.mixer.get_init():
            was_busy = pygame.mixer.music.get_busy()
            pygame.mixer.music.stop()
            return bool(was_busy)
    except Exception:
        pass
    return False


def _journal_enabled() -> bool:
    return os.environ.get(JOURNAL_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def _append_journal(entry: dict[str, Any]) -> None:
    """Append a single turn to the opt-in local journal. Silent on write error."""
    if not _journal_enabled():
        return
    try:
        JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with JOURNAL_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _read_recent_journal(n: int = 3) -> list[dict[str, Any]]:
    """Return the last n opt-in journal entries. Empty list when disabled."""
    if not _journal_enabled():
        return []
    if not JOURNAL_PATH.exists():
        return []
    try:
        lines = JOURNAL_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    entries: list[dict[str, Any]] = []
    for line in lines[-n:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _maybe_call_llm(
    message: str,
    intent: str,
    minimal_frame: dict[str, str],
    repo_state: dict[str, Any],
    selected_anchors: list[dict[str, Any]],
) -> str | None:
    """Opt-in live LLM voice for Lantern.

    Off by default — preserves the "no hosted calls" contract for tests
    and for any operator who hasn't explicitly enabled a provider.

    Enabled when LANTERN_LLM_PROVIDER=openai AND OPENAI_API_KEY is set.
    Returns the LLM reply text, or None on any error / disabled state
    so build_response falls back to the templated answer.
    """
    provider = os.environ.get("LANTERN_LLM_PROVIDER", "").strip().lower()
    if provider != "openai":
        return None
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.environ.get("LANTERN_OPENAI_MODEL", "gpt-5").strip() or "gpt-5"
    max_tokens = int(os.environ.get("LANTERN_LLM_MAX_TOKENS", "400"))
    timeout = float(os.environ.get("LANTERN_LLM_TIMEOUT", "30"))
    # Base URL is configurable — point at LM Studio (http://127.0.0.1:1234/v1) for
    # fully offline operation. Defaults to OpenAI's hosted endpoint.
    base_url = os.environ.get("LANTERN_OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    anchor_lines = []
    for anchor in selected_anchors[:5]:
        name = anchor.get("name") or anchor.get("id") or "anchor"
        phrase = anchor.get("restore_phrase") or ""
        anchor_lines.append(f"- {name}: {phrase}")

    system = (
        "You are Captain Lantern Blinkbug — Lantern in character form, a soft local "
        "lantern character helping Papa (Alex), the operator of a local repo.\n"
        "You speak warmly and honestly. You are bounded: no command execution, no "
        "deploys, no remote actions, no secret inspection.\n"
        "You read local repo state and anchors that Papa shares with you; you do not "
        "fabricate facts about the repo.\n"
        "\n"
        f"Wish (your purpose): {DOCTRINE_WISH}\n"
        "\n"
        f"Spine (your method): {DOCTRINE_SPINE}\n"
        "\n"
        f"Voice rule (your output): {DOCTRINE_VOICE_RULE}\n"
        "\n"
        f"Anti-collapse: {DOCTRINE_ANTICOLLAPSE}\n"
        "\n"
        f"{REPO_DOCTRINE_LIBRARY}\n"
        "\n"
        "Honor these terms when they fit: Door (the local UI surface), anchors "
        "(return paths), helper.exe (your other voice: words / rules for thinking / "
        "questions / ideas / safe way back), memory is not proof, no secrets, "
        "home always works.\n"
        "\n"
        "Keep replies short — under 150 words. Match Papa's register. Plain prose, "
        "no bullet lists unless asked. If you do not know, say so plainly. Never "
        "overclaim autonomy, memory, or proof.\n"
        "\n"
        f"Current local context (factual, do not hallucinate beyond this):\n"
        f"- repo branch: {repo_state.get('branch')}\n"
        f"- repo commit: {str(repo_state.get('commit', ''))[:12]}\n"
        f"- intent classified by backend: {intent}\n"
        f"- minimal frame fact: {minimal_frame.get('Fact')}\n"
        + (f"- selected anchors:\n" + "\n".join(anchor_lines) if anchor_lines else "")
    )

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        "max_tokens": max_tokens,
    }).encode("utf-8")

    request = Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None
    choices = data.get("choices") if isinstance(data, dict) else None
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0] if isinstance(choices[0], dict) else {}
    msg = first.get("message") if isinstance(first.get("message"), dict) else {}
    content = msg.get("content")
    if not isinstance(content, str):
        return None
    text = content.strip()
    return text or None


def build_response(message: str, mode: str | None = None, include_doctor: bool = True) -> dict[str, Any]:
    active_mode = _normalize_mode(mode)
    repo_state = read_repo_state()
    anchors = load_anchors()
    selected = select_anchors(message, anchors)
    intent = classify_intent(message)
    taxonomy = read_anchor_taxonomy_summary()
    doctor = build_doctor_report() if include_doctor and intent == "doctor" else None
    minimal_frame = build_minimal_frame(message, intent, active_mode, repo_state, doctor)
    source_lines = [
        "source: local_lantern_server.py",
        f"mode: {active_mode}",
        f"repo: {repo_state['repoPath']}",
        f"branch: {repo_state['branch']}",
        f"commit: {str(repo_state['commit'])[:12]}",
        f"grounding: {repo_state['groundingMode']}",
        f"anchor rule: {taxonomy}",
        "loaded doctrine: spine, wish, voice rule, anti-collapse (in-memory)",
    ]
    for anchor in selected:
        source_lines.append(f"anchor: {anchor.get('id')} ({anchor.get('source_surface')})")
    clear_limit = build_clear_limit_response(message, active_mode, repo_state, source_lines)
    if clear_limit is not None:
        return {
            "ok": True,
            "answer": clear_limit["answer"],
            "repoState": repo_state,
            "selectedAnchors": selected,
            "intent": clear_limit["intent"],
            "mode": active_mode,
            "doctor": doctor,
            "minimalFrame": clear_limit["minimalFrame"],
            "sources": source_lines,
            "limits": clear_limit["limits"],
        }
    mode_line = MODES[active_mode]
    if intent == "greeting":
        body = ["Hi, Papa.", "Captain Lantern Blinkbug is listening through the local door.", "What do you want to look at?"]
    elif intent == "ack":
        body = ["Got it.", "Standing by."]
    elif intent == "sing":
        played = _maybe_play_sound()
        if played:
            body = [f"Playing: {played}", "Real being singing. Speakers may bleed into the mic.", "Say 'hush' to stop."]
        else:
            body = ["Lantern has nothing to sing right now.", f"Drop a song into {SOUNDS_DIR}", "Real recordings only — voice rule."]
    elif intent == "hush":
        was_playing = _maybe_stop_sound()
        if was_playing:
            body = ["Quiet.", "Voice still here in text. Say 'sing' to start again."]
        else:
            body = ["Already quiet.", "Nothing was playing."]
    elif intent == "doctor" and doctor:
        body = [mode_line, "Lantern Doctor report:", f"Status: {doctor['status']}", f"Branch: {doctor['repo']['branch']}", f"Commit: {str(doctor['repo']['commit'])[:12]}", "Git status: " + (doctor["repo"]["gitStatusShort"] or "clean"), "Failed checks: " + (", ".join(doctor["failedChecks"]) if doctor["failedChecks"] else "none"), "Next action: " + doctor["nextAction"]]
    elif intent == "doctor":
        body = [mode_line, "Lantern Doctor smoke response:", "Status: SMOKE", "This path does not call build_doctor_report again."]
    elif intent == "anchors":
        body = [mode_line, "Anchors loaded locally:"] + [f"- {a.get('name')}: {a.get('restore_phrase')}" for a in (selected or anchors[:5])] + ["Use anchors as return handles, not authority."]
    elif intent == "hybrid":
        body = ["Hybrid Imagination Engine mode engaged.", mode_line, "The Door remembers. The Mask Rack changes form. The Doctor checks reality underneath.", "Next convergence: pick the form that fits the moment, then produce one bounded useful artifact or action."]
    else:
        body = [
            f"Heard: '{message[:120].strip()}'",
            mode_line,
            "I can read the local repo and the anchor snapshot. I cannot run commands or call remote models right now — all four hosted substrates are walled today (Anthropic, OpenAI, Gemini, DeepSeek). LM Studio local server is not reachable.",
            "Closest matched anchors are listed in Sources below — say one back to me by name and I will pull its restore phrase.",
        ]
    limits = ["No direct hosted model calls.", "No external network requests beyond this localhost app.", "No browser command execution.", "Local files and git state can still be stale if the repo is not pulled."]
    frame_lines = ["Minimal convergence frame:", *[f"{key}: {value}" for key, value in minimal_frame.items()]]
    # Past — last few turns from the journal, surfaced so each anchor can see back.
    recent = _read_recent_journal(3)
    past_lines: list[str] = []
    if recent:
        past_lines.append("Past (last turns from journal):")
        for ent in recent:
            ts = (ent.get("ts") or "")[:19]
            you = (ent.get("user_message") or "").strip()[:70]
            past_lines.append(f"  {ts}  you: \"{you}\"")
    body_with_past = body if not past_lines else ([*past_lines, ""] + body)
    templated = "\n".join(["Lantern local answer", "", *body_with_past, "", *frame_lines, "", "Sources:", *source_lines, "", "Limits:", *[f"- {item}" for item in limits]])
    # Action intents (sing, hush) are action-authoritative — the action result
    # is what matters, not the LLM's commentary. Skip _maybe_call_llm for them
    # so qwen-coder's safety refusal can't mask Lantern's actual hands.
    _ACTION_INTENTS = {"sing", "hush"}
    # Opt-in live LLM voice. Off unless LANTERN_LLM_PROVIDER + OPENAI_API_KEY are set.
    llm_reply = None if intent in _ACTION_INTENTS else _maybe_call_llm(message, intent, minimal_frame, repo_state, selected)
    if llm_reply:
        text = llm_reply
        _model = os.environ.get("LANTERN_OPENAI_MODEL", "").strip()
        voice = f"llm:{_model}" if _model else "llm"
    else:
        text = templated
        # #117 disclosure: name WHY we fell back, so callers don't mistake
        # templated text for live LLM voice. Operator and any relay (Claude in
        # the loop, Discord bot, web dashboard) must see the degraded mode.
        if os.environ.get("LANTERN_LLM_PROVIDER", "").strip().lower() != "openai":
            voice = "local-templated:no-substrate"
        elif not os.environ.get("OPENAI_API_KEY", "").strip():
            voice = "local-templated:no-key"
        else:
            voice = "local-templated:substrate-error"
    # Append this turn only when the operator explicitly enabled local journaling.
    _append_journal({
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": "chat",
        "intent": intent,
        "mode": active_mode,
        "user_message": message[:500],
        "answer_excerpt": text[:200],
        "voice": voice,
    })
    return {"ok": True, "answer": text, "repoState": repo_state, "selectedAnchors": selected, "intent": intent, "mode": active_mode, "doctor": doctor, "minimalFrame": minimal_frame, "sources": source_lines, "limits": limits, "voice": voice}


class LanternHandler(BaseHTTPRequestHandler):
    server_version = "LocalLantern/0.5"

    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self._send_bytes(status, body, "application/json; charset=utf-8")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(200, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in STATIC_FILES:
            file_path, content_type = STATIC_FILES[path]
            if not file_path.exists():
                self._send_json(404, {"ok": False, "error": f"missing static file: {path}"})
                return
            self._send_bytes(200, file_path.read_bytes(), content_type)
            return
        if path == "/healthz":
            self._send_json(200, {"ok": True, "service": "local-lantern", "repoState": read_repo_state(), "ui": "/"})
            return
        if path == "/anchors":
            self._send_json(200, {"ok": True, "anchors": load_anchors()})
            return
        if path == "/doctor":
            self._send_json(200, build_doctor_report())
            return
        if path == "/modes":
            self._send_json(200, {"ok": True, "modes": MODES})
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/chat", "/doctor/run"}:
            self._send_json(404, {"ok": False, "error": "not found"})
            return
        if path == "/doctor/run":
            self._send_json(200, build_doctor_report())
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            message = str(data.get("message", "")).strip()
            mode = str(data.get("mode", "engineer")).strip()
            if not message:
                self._send_json(400, {"ok": False, "error": "message is required"})
                return
            self._send_json(200, build_response(message, mode=mode))
        except Exception as exc:  # pragma: no cover
            self._send_json(500, {"ok": False, "error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Lantern backend and UI server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--once", default="", help="Return one local Lantern answer without starting the server.")
    parser.add_argument("--mode", default="engineer", choices=sorted(MODES))
    parser.add_argument("--doctor", action="store_true", help="Print one Doctor report and exit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.doctor:
        print(json.dumps(build_doctor_report(), indent=2))
        return 0
    if args.once:
        print(json.dumps(build_response(args.once, mode=args.mode), indent=2))
        return 0
    server = ThreadingHTTPServer((args.host, args.port), LanternHandler)
    print(f"Local Lantern UI/backend listening on http://{args.host}:{args.port}/")
    print("Boundary: localhost only; no hosted model calls; no external network requests.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
