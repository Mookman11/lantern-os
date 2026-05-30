from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_discord_health_script_has_p0_voice_gate() -> None:
    text = read("scripts/Test-DiscordBotHealth.ps1")
    required = [
        "LANTERN_VOICE_CHANNEL",
        "LANTERN_VOICE_CHANNEL_ID",
        "discord_py_dependency",
        "pynacl_voice_dependency",
        "ffmpeg_dependency",
        "voice_target_env",
        "voice_channel_access",
        "/guilds/$guildId/channels",
        "P0 blocked",
        "adding Lantern to Lounge",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_discord_lounge_bot_has_bounded_voice_commands() -> None:
    text = read("src/discord_lounge_bot/bot.py")
    required = [
        "LANTERN_DISCORD_ENABLE_VOICE",
        "LANTERN_DISCORD_ENABLE_RADIO",
        "LANTERN_RADIO_URL",
        "LANTERN_VOICE_CHANNEL",
        "!lantern-voice-check",
        "!lantern-join-lounge",
        "!lantern-leave-lounge",
        "!lantern-radio",
        "no auto-join, no autoplay, no shell/MCP execution from Discord",
        "rights-checked source",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_discord_voice_deps_and_docs_reference_frank_lounge_path() -> None:
    requirements = read("src/discord_lounge_bot/requirements.txt")
    readme = read("src/discord_lounge_bot/README.md")
    assert "discord.py[voice]" in requirements
    required = [
        "P0-gated voice/radio access",
        "LANTERN_VOICE_CHANNEL",
        "LANTERN_VOICE_CHANNEL_ID",
        "PyNaCl",
        "ffmpeg",
        "Frank Sinatra/Rhythm lane",
        "lantern-tutorial-frank.html",
        "do not auto-stream",
        "rights-checked stream or local file",
    ]
    missing = [phrase for phrase in required if phrase not in readme]
    assert missing == []
