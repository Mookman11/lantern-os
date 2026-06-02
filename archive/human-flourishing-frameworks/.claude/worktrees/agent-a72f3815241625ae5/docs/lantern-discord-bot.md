# Lantern Discord Bot

Status: bounded adapter design.

## Purpose

The Lantern Discord bot lets an approved Discord server ask the local Lantern
desktop runtime through a slash command. It is an adapter to Lantern, not a new
authority surface.

## Default boundary

```text
slash-command first
local Lantern endpoint only by default
no raw transcript storage
no DM support
no autonomous moderation
no repo actions
no deployments
no agents
no tunnels
no sensors
no command execution
no public writes outside the invoking Discord response
```

## Runtime shape

```text
Discord /lantern command
-> input provenance wrapper
-> local Lantern desktop server POST /chat
-> Discord reply
```

Default local endpoint:

```text
http://127.0.0.1:8765/chat
```

Lantern keeps its own boundaries: text-only response, no command execution, no
repo writes, no agents, no tunnels, and no deployments.

## Discord Developer Portal setup

Register the bot in Discord first:

```text
1. Create a Discord application.
2. Add a bot user.
3. Copy the bot token into a local environment variable only.
4. OAuth2 URL Generator scopes: bot + applications.commands.
5. Bot permissions: Send Messages is enough for basic slash-command replies.
6. Keep Message Content Intent disabled unless LANTERN_DISCORD_ENABLE_MENTIONS=true.
```

Never commit the token.

## Required environment

PowerShell:

```powershell
$env:DISCORD_BOT_TOKEN="paste-token-here"
```

cmd.exe:

```bat
set DISCORD_BOT_TOKEN=paste-token-here
```

## Optional environment

```text
LANTERN_DISCORD_ENDPOINT=http://127.0.0.1:8765
LANTERN_DISCORD_CHAT_PATH=/chat
LANTERN_DISCORD_MODE=engineer
LANTERN_DISCORD_ALLOWED_GUILDS=123,456
LANTERN_DISCORD_ALLOWED_CHANNELS=789,101112
LANTERN_DISCORD_EPHEMERAL=true
LANTERN_DISCORD_ENABLE_MENTIONS=false
LANTERN_DISCORD_ALLOW_REMOTE=false
LANTERN_DISCORD_TIMEOUT_SECONDS=30
```

## Install

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-discord.txt
```

## Run

Start local Lantern desktop server first:

```powershell
.\scripts\start_lantern_local_chat.bat
```

Expected local URL:

```text
http://127.0.0.1:8765/
```

Health check:

```text
http://127.0.0.1:8765/healthz
```

Then start the Discord adapter in another terminal:

```bash
python -m lantern.discord_bot
```

The adapter defaults to:

```text
LANTERN_DISCORD_ENDPOINT=http://127.0.0.1:8765
LANTERN_DISCORD_CHAT_PATH=/chat
```

## Commands

```text
/lantern prompt:<text>
```

Mention support is disabled by default. If `LANTERN_DISCORD_ENABLE_MENTIONS=true`,
the bot can also answer direct mentions in allowed channels. This requires the
Discord message-content intent and should stay disabled unless explicitly needed.

## Provenance wrapper

Every Discord prompt is wrapped with:

```text
INPUT PROVENANCE: DISCORD_SLASH_COMMAND | DISCORD_MENTION
SURFACE: Discord Lantern adapter
GUILD_ID
CHANNEL_ID
USER_ID
Boundary
User message
```

The wrapper tells Lantern not to treat Discord input as automatic operator
authority and not to infer approval to merge, deploy, spend money, contact third
parties, use secrets, start agents, run commands, or enable sensors.

## Remote endpoint rule

By default, only local endpoints are allowed:

```text
http://127.0.0.1:8765
http://localhost:8765
http://[::1]:8765
```

Remote endpoints require `LANTERN_DISCORD_ALLOW_REMOTE=true` and separate tunnel
review. Verify tunnels before trusting remote endpoints.

## Stop conditions

Stop the adapter if:

```text
Discord token leaks
unexpected public channel replies appear
Lantern endpoint is remote without review
message-content intent was enabled accidentally
bot is added to an unapproved guild
responses imply repo writes, deployments, agents, tunnels, or command execution
users treat the bot as medical/legal/financial/emergency authority
```

## Validation

```bash
python -m unittest tests.test_lantern_discord_bot -v
python -m unittest discover -s tests -t .
```
