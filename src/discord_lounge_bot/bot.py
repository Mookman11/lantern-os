"""
Lantern Discord Lounge Bot

Status-only bot for one allowlisted channel:
- posts startup status in the configured channel;
- replies to !lantern-status with a safe health summary;
- ignores all other channels.
"""

import os
import shutil
import sys
from datetime import datetime, timezone

try:
    import discord
except Exception as exc:
    print(f"[FATAL] Missing dependency 'discord.py': {exc}")
    print("Install with: pip install discord.py")
    sys.exit(1)


TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
GUILD_ID = os.getenv("LANTERN_DISCORD_GUILD_ID", "").strip()
CHANNEL_ID = os.getenv("LANTERN_DISCORD_CHANNEL_ID", "").strip()
STATUS_URL = os.getenv("LANTERN_STATUS_URL", "http://127.0.0.1:5001/api/status").strip()
VOICE_CHANNEL_ID = os.getenv("LANTERN_VOICE_CHANNEL_ID", "").strip()
VOICE_CHANNEL_NAME = os.getenv("LANTERN_VOICE_CHANNEL", "Lounge").strip()
RADIO_URL = os.getenv("LANTERN_RADIO_URL", "").strip()
ENABLE_VOICE = os.getenv("LANTERN_DISCORD_ENABLE_VOICE", "").strip().lower() in {"1", "true", "yes", "on"}
ENABLE_RADIO = os.getenv("LANTERN_DISCORD_ENABLE_RADIO", "").strip().lower() in {"1", "true", "yes", "on"}

if not TOKEN:
    print("[FATAL] Missing DISCORD_BOT_TOKEN")
    sys.exit(1)
if not GUILD_ID:
    print("[FATAL] Missing LANTERN_DISCORD_GUILD_ID")
    sys.exit(1)
if not CHANNEL_ID:
    print("[FATAL] Missing LANTERN_DISCORD_CHANNEL_ID")
    sys.exit(1)

try:
    GUILD_ID_INT = int(GUILD_ID)
    CHANNEL_ID_INT = int(CHANNEL_ID)
except ValueError:
    print("[FATAL] Guild/channel IDs must be numeric Discord snowflakes.")
    sys.exit(1)

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def status_text() -> str:
    return (
        "Lantern lounge bot online.\n"
        f"- time: {now_utc()}\n"
        f"- guild: {GUILD_ID_INT}\n"
        f"- channel: {CHANNEL_ID_INT}\n"
        f"- local status endpoint: {STATUS_URL}\n"
        "- commands: !lantern-status, !lantern-voice-check"
    )


def voice_status_text() -> str:
    target = VOICE_CHANNEL_ID or VOICE_CHANNEL_NAME or "not configured"
    return (
        "Lantern voice gate.\n"
        f"- target: {target}\n"
        f"- voice enabled: {ENABLE_VOICE}\n"
        f"- radio enabled: {ENABLE_RADIO}\n"
        f"- radio url configured: {bool(RADIO_URL)}\n"
        f"- ffmpeg on PATH: {bool(shutil.which('ffmpeg'))}\n"
        "- join command: !lantern-join-lounge\n"
        "- radio command: !lantern-radio\n"
        "- boundary: no auto-join, no autoplay, no shell/MCP execution from Discord"
    )


def find_voice_channel(guild: discord.Guild):
    if VOICE_CHANNEL_ID:
        try:
            channel_id = int(VOICE_CHANNEL_ID)
        except ValueError:
            return None
        return discord.utils.get(guild.voice_channels, id=channel_id)
    if VOICE_CHANNEL_NAME:
        return discord.utils.find(lambda channel: channel.name.lower() == VOICE_CHANNEL_NAME.lower(), guild.voice_channels)
    return None


async def connect_to_lounge(message: discord.Message):
    if not ENABLE_VOICE:
        await message.reply("Voice join is held. Set LANTERN_DISCORD_ENABLE_VOICE=true after P0 health checks pass.")
        return None
    if message.guild is None:
        await message.reply("Voice join needs a guild context.")
        return None
    channel = find_voice_channel(message.guild)
    if channel is None:
        await message.reply("Configured Lounge voice channel was not found. Run Test-DiscordBotHealth.ps1 first.")
        return None
    if message.guild.voice_client and message.guild.voice_client.is_connected():
        await message.reply(f"Lantern is already connected to {message.guild.voice_client.channel.name}.")
        return message.guild.voice_client
    voice_client = await channel.connect()
    await message.reply(f"Lantern joined {channel.name}.")
    return voice_client


@client.event
async def on_ready():
    print(f"[READY] Logged in as {client.user} at {now_utc()}")
    channel = client.get_channel(CHANNEL_ID_INT)
    if channel is None:
        print("[WARN] Configured channel was not found in cache. Check bot permissions and IDs.")
        return
    try:
        await channel.send(status_text())
    except Exception as exc:
        print(f"[WARN] Failed to send startup status message: {exc}")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.channel.id != CHANNEL_ID_INT:
        return
    content = message.content.strip().lower()
    if content == "!lantern-status":
        await message.reply(status_text())
    elif content == "!lantern-voice-check":
        await message.reply(voice_status_text())
    elif content == "!lantern-join-lounge":
        await connect_to_lounge(message)
    elif content == "!lantern-leave-lounge":
        if message.guild and message.guild.voice_client and message.guild.voice_client.is_connected():
            await message.guild.voice_client.disconnect()
            await message.reply("Lantern left Lounge.")
        else:
            await message.reply("Lantern is not connected to a voice channel.")
    elif content == "!lantern-radio":
        if not ENABLE_RADIO:
            await message.reply("Radio is held. Set LANTERN_DISCORD_ENABLE_RADIO=true and LANTERN_RADIO_URL after rights and P0 checks pass.")
            return
        if not RADIO_URL:
            await message.reply("Radio URL is not configured. Set LANTERN_RADIO_URL to a rights-checked stream or local file.")
            return
        if not shutil.which("ffmpeg"):
            await message.reply("ffmpeg is missing on PATH, so radio playback is blocked.")
            return
        voice_client = await connect_to_lounge(message)
        if voice_client is None:
            return
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio(RADIO_URL))
        await message.reply("Lantern radio started from the configured rights-checked source.")


def main():
    print("[INFO] Starting Lantern Discord lounge bot...")
    print("[INFO] No secrets are printed. Stop with Ctrl+C.")
    client.run(TOKEN)


if __name__ == "__main__":
    main()
