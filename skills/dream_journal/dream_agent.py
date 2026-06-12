"""
Hybrid Dream Journal agent.

Uses the official OpenAI Agents SDK when it is available, while keeping the
Lantern OS memory and cognitive layers usable offline. The fallback path is
intentional: Dream Journal should still log, recall, and mirror dreams without
network access or an API key.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Load local env overrides if present
_repo_root = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv
    load_dotenv(_repo_root / ".env.local")
except Exception:
    pass

try:
    from agents import Agent, Runner
except Exception:  # pragma: no cover - optional SDK boundary
    Agent = None
    Runner = None

from .cognitive_layer import CognitiveJournal
from .dream_journal import DreamJournal

# Bridge to unified connector if available
try:
    from src.unified_agent_connector import UnifiedAgentConnector, get_connector
except Exception:
    UnifiedAgentConnector = None  # type: ignore
    get_connector = None  # type: ignore


SYSTEM_PROMPT = """You are Dream Journal inside Lantern OS.
Stay grounded, concise, and privacy-preserving. Treat dream interpretation as
reflection, not diagnosis. Use memory only as context and never claim certainty.
Offer one useful next question or action."""


@dataclass
class DreamAgentResult:
    reply: str
    source: str
    fallacies: List[Dict[str, Any]]
    recent_count: int
    agent_runtime: str
    held: bool = False


class DreamAgent:
    """Hybrid reasoning + local memory facade for Dream Journal v2."""

    def __init__(
        self,
        data_dir: str = "data/dream_journal",
        model: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        enable_sdk: Optional[bool] = None,
        require_agent_runtime: bool = True,
    ) -> None:
        self.journal = DreamJournal(data_dir=data_dir)
        self.cognitive = CognitiveJournal(data_dir=data_dir)
        self.model = model or os.environ.get("DREAM_AGENT_MODEL") or os.environ.get("OLLAMA_MODEL") or "llama3.2"
        self.ollama_base_url = (ollama_base_url or os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
        self.require_agent_runtime = require_agent_runtime
        self.enable_sdk = (
            os.environ.get("DREAM_AGENT_ENABLE_OPENAI", "").lower() in ("1", "true", "yes")
            and bool(os.environ.get("OPENAI_API_KEY"))
            if enable_sdk is None
            else enable_sdk
        )
        self._agent = None

        if self.enable_sdk and Agent is not None:
            self._agent = Agent(
                name="Lantern Dream Journal",
                instructions=SYSTEM_PROMPT,
                model=model,
            )

    def log_dream(
        self,
        content: str,
        lucidity: float = 0.0,
        emotions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        linked_goals: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Append a structured dream to local JSONL storage."""
        return self.journal.log_dream(
            content=content,
            lucidity=lucidity,
            emotions=emotions,
            tags=tags,
            linked_goals=linked_goals,
        )

    def recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent local dreams."""
        return self.journal.get_recent(limit)

    def mirror(self, text: str, provider: Optional[str] = None, persona: Optional[str] = None) -> DreamAgentResult:
        """Reflect on text through the best available agent runtime."""
        fallacies = self.cognitive.analyze(text)
        recent = self.recent(3)
        context = self._build_context(text, fallacies, recent)

        # 1. Unified connector (multi-provider, slot-aware)
        if get_connector is not None:
            try:
                connector = get_connector()
                out = []
                meta = {}
                gen = connector.stream(text, persona_id=persona, provider=provider, context=context)
                while True:
                    try:
                        token = next(gen)
                        if isinstance(token, str):
                            out.append(token)
                        else:
                            meta = dict(token) if hasattr(token, "items") else {}
                    except StopIteration as exc:
                        if exc.value and isinstance(exc.value, dict):
                            meta = exc.value
                        break
                reply = "".join(out)
                if reply:
                    return DreamAgentResult(
                        reply=reply,
                        source=meta.get("provider", "unified"),
                        fallacies=fallacies,
                        recent_count=len(recent),
                        agent_runtime=meta.get("provider", "unified"),
                    )
            except Exception as exc:
                print(f"[warn] Unified connector failed: {exc}")

        # 2. Legacy Ollama fallback
        prompt = self._build_prompt(text, fallacies, recent)
        ollama_reply = self._run_ollama(prompt)
        if ollama_reply is not None:
            return DreamAgentResult(
                reply=ollama_reply,
                source="ollama_local_agent",
                fallacies=fallacies,
                recent_count=len(recent),
                agent_runtime=f"ollama:{self.model}",
            )

        # 3. OpenAI Agents SDK fallback
        if self._agent is not None and Runner is not None:
            try:
                result = Runner.run_sync(self._agent, prompt)
                return DreamAgentResult(
                    reply=str(result.final_output),
                    source="openai_agents_sdk",
                    fallacies=fallacies,
                    recent_count=len(recent),
                    agent_runtime=f"openai_agents:{self.model}",
                )
            except Exception as exc:
                return DreamAgentResult(
                    reply=self._held_reply(f"OpenAI Agents SDK failed after local Ollama was unavailable: {exc}"),
                    source="held_no_agent_runtime",
                    fallacies=fallacies,
                    recent_count=len(recent),
                    agent_runtime="none",
                    held=True,
                )

        if self.require_agent_runtime:
            return DreamAgentResult(
                reply=self._held_reply("No agent runtime responded."),
                source="held_no_agent_runtime",
                fallacies=fallacies,
                recent_count=len(recent),
                agent_runtime="none",
                held=True,
            )

        return DreamAgentResult(
            reply=self._diagnostic_only_reply(text, fallacies, recent),
            source="diagnostic_only_not_dreamer",
            fallacies=fallacies,
            recent_count=len(recent),
            agent_runtime="none",
            held=True,
        )

    def talk_to_character(self, character: str, message: str, user_id: str = "operator") -> str:
        """Route a message through persistent symbolic character memory."""
        return self.cognitive.talk(character, message, user_id=user_id)

    def _build_prompt(
        self,
        text: str,
        fallacies: List[Dict[str, Any]],
        recent: List[Dict[str, Any]],
    ) -> str:
        recent_lines = [
            f"- {item.get('timestamp', 'unknown')}: {item.get('content') or item.get('text', '')[:180]}"
            for item in recent
        ]
        return "\n".join([
            SYSTEM_PROMPT,
            "",
            "Reflect on this dream or dream-adjacent note:",
            text,
            "",
            f"Local fallacy hints: {fallacies}",
            "Recent local dream context:",
            "\n".join(recent_lines) if recent_lines else "- none",
            "",
            "Return: one mirror, one grounded interpretation, one next question.",
        ])

    def _build_context(self, text: str, fallacies: List[Dict[str, Any]], recent: List[Dict[str, Any]]) -> str:
        """Build context string for unified connector (not a full prompt)."""
        recent_lines = [
            f"- {item.get('timestamp', 'unknown')}: {item.get('content') or item.get('text', '')[:180]}"
            for item in recent
        ]
        parts = [
            f"Dreamer input: {text}",
            f"Local fallacy hints: {fallacies}",
        ]
        if recent_lines:
            parts.append("Recent local dream context:\n" + "\n".join(recent_lines))
        return "\n".join(parts)

    def _run_ollama(self, prompt: str) -> Optional[str]:
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 450,
            },
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.ollama_base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return None
        reply = str(data.get("response", "")).strip()
        return reply or None

    def _held_reply(self, reason: str) -> str:
        return (
            "Dreamer agent held: no live agent runtime is available. "
            f"{reason} Start Ollama and pull the configured model before using DreamAgent as a Dreamer."
        )

    def _diagnostic_only_reply(
        self,
        text: str,
        fallacies: List[Dict[str, Any]],
        recent: List[Dict[str, Any]],
    ) -> str:
        fallacy_line = ""
        if fallacies:
            names = ", ".join(item.get("fallacy", "unknown") for item in fallacies[:3])
            fallacy_line = f" Reasoning pattern to check: {names}."
        recent_line = f" I can see {len(recent)} recent local dream(s)." if recent else ""
        return (
            f"Diagnostic only, not Dreamer speech. Input preview: {text[:240]}"
            f"{recent_line}{fallacy_line} "
            "A real Dreamer reply requires Ollama or another configured agent runtime."
        )


def get_dream_agent() -> DreamAgent:
    """Convenience factory for API routes and local scripts."""
    return DreamAgent()
