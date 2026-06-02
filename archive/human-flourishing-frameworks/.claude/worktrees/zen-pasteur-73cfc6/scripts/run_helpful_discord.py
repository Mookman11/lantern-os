#!/usr/bin/env python3
"""Run Lantern Discord with helpful public replies.

This keeps the existing Discord adapter boundaries, but patches the public reply
formatting so local Lantern answers are sanitized instead of flattened into the
same generic "Lantern is online" card.

Boundaries remain: text-only replies, local endpoint by default, no moderation,
no transcript storage, no command execution, no repo actions, no agents, no
sensors, no claim that Lantern physically completed a task.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lantern import discord_bot  # noqa: E402

_STOP_MARKERS = (
    "\nMinimal convergence frame:",
    "\nSources:",
    "\nLimits:",
)


def _strip_internal_sections(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("Lantern local answer"):
        cleaned = cleaned[len("Lantern local answer"):].strip()
    for marker in _STOP_MARKERS:
        index = cleaned.find(marker)
        if index >= 0:
            cleaned = cleaned[:index].strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _fallback_next_step(text: str) -> str:
    lower = text.lower()
    if "trash" in lower or "garbage" in lower:
        return (
            "Trash signal received. I can't carry it physically, but I can make the next step clear: "
            "tie the bag, check bathroom/kitchen bins, take it out before the next transition, then come back and say 'trash out.'"
        )
    return (
        "Lantern is online. Give me one concrete target and I will answer with one practical next step, "
        "while staying text-only and bounded."
    )


def helpful_public_reply(response: discord_bot.LanternResponse) -> str:
    if response.status.startswith("lantern_"):
        return (
            "Lantern is connected to Discord, but the local Lantern server is not reachable right now. "
            "Check that the local Lantern server window is open and that the configured port is correct."
        )

    reply = _strip_internal_sections(response.reply)
    if not reply or reply == "Lantern returned no text reply.":
        reply = _fallback_next_step(str(response.raw))

    return reply[: discord_bot.MAX_DISCORD_MESSAGE_CHARS]


def helpful_discord_reply(response: discord_bot.LanternResponse) -> str:
    text = helpful_public_reply(response)
    if response.model:
        return f"Lantern status: {response.status} | model: {response.model}\n\n{text}"
    return f"Lantern status: {response.status}\n\n{text}"


def build_helpful_lantern_message(
    user_text: str,
    *,
    provenance: str,
    guild_id: int | None,
    channel_id: int | None,
    user_id: int | None,
) -> str:
    clean = user_text.strip()
    return (
        "Discord Lantern prompt.\n"
        f"Provenance: {provenance}. Guild={guild_id}; Channel={channel_id}; User={user_id}.\n"
        "Boundary: answer text-only; do not moderate, store private chats, run commands, use secrets, "
        "start agents, contact third parties, enable sensors, or claim physical action.\n"
        "For practical household logistics, give one concrete next step and a return cue.\n\n"
        f"User message: {clean}"
    )


def patch_adapter() -> None:
    discord_bot.format_public_lantern_reply = helpful_public_reply  # type: ignore[assignment]
    discord_bot.format_discord_reply = helpful_discord_reply  # type: ignore[assignment]
    discord_bot.build_lantern_message = build_helpful_lantern_message  # type: ignore[assignment]


def main() -> int:
    patch_adapter()
    return discord_bot.main()


if __name__ == "__main__":
    raise SystemExit(main())
