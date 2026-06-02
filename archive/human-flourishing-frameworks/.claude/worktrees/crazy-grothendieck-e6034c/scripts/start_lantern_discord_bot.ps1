<#
.SYNOPSIS
Start the Lantern Discord bot on Windows with local encrypted token storage.

.DESCRIPTION
This launcher stores the Discord bot token using PowerShell's Export-Clixml
SecureString behavior. On Windows, that uses DPAPI protection tied to the current
Windows user account and machine.

The token is not committed, not printed, and not written as plaintext. It is
loaded into DISCORD_BOT_TOKEN only for this child process.

Usage:

  .\scripts\start_lantern_discord_bot.ps1 -Endpoint http://127.0.0.1:8766
  .\scripts\start_lantern_discord_bot.ps1 -ResetToken -Endpoint http://127.0.0.1:8766

Boundary:
- local token file under %APPDATA%\Lantern;
- token encrypted for the current Windows user/machine;
- no plaintext .env file;
- no token echo;
- no token commit;
- starts only the Discord adapter process.
#>

[CmdletBinding()]
param(
    [string]$Endpoint = "http://127.0.0.1:8765",
    [string]$ChatPath = "/chat",
    [string]$Mode = "engineer",
    [switch]$ResetToken,
    [switch]$PublicReplies,
    [switch]$EnableMentions
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    $scriptDir = Split-Path -Parent $PSCommandPath
    return (Resolve-Path (Join-Path $scriptDir "..")).Path
}

function Get-TokenStorePath {
    $dir = Join-Path $env:APPDATA "Lantern"
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
    return Join-Path $dir "discord-bot-token.secure.xml"
}

function Save-TokenSecurely {
    param([string]$Path)

    Write-Host "Lantern Discord token setup"
    Write-Host "Paste the Bot token from Discord Developer Portal > Applications > Lantern > Bot > Token."
    Write-Host "Input is hidden. The token will be encrypted for this Windows user and stored at:"
    Write-Host "  $Path"

    $secure = Read-Host "Discord Bot token" -AsSecureString
    if ($null -eq $secure -or $secure.Length -eq 0) {
        throw "No token entered."
    }
    $secure | Export-Clixml -Path $Path
    Write-Host "Saved encrypted token for this Windows user."
}

function Convert-SecureStringToPlainText {
    param([System.Security.SecureString]$SecureString)

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureString)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        if ($bstr -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }
}

$repoRoot = Get-RepoRoot
$tokenPath = Get-TokenStorePath

if ($ResetToken -and (Test-Path $tokenPath)) {
    Remove-Item $tokenPath -Force
    Write-Host "Removed existing encrypted token."
}

if (-not (Test-Path $tokenPath)) {
    Save-TokenSecurely -Path $tokenPath
}

$secureToken = Import-Clixml -Path $tokenPath
if ($null -eq $secureToken) {
    throw "Token store is empty or unreadable. Use -ResetToken."
}

$plainToken = Convert-SecureStringToPlainText -SecureString $secureToken
if ([string]::IsNullOrWhiteSpace($plainToken)) {
    throw "Token decrypted to an empty value. Use -ResetToken."
}

try {
    Push-Location $repoRoot

    $env:DISCORD_BOT_TOKEN = $plainToken
    $env:LANTERN_DISCORD_ENDPOINT = $Endpoint
    $env:LANTERN_DISCORD_CHAT_PATH = $ChatPath
    $env:LANTERN_DISCORD_MODE = $Mode
    $env:LANTERN_DISCORD_EPHEMERAL = if ($PublicReplies) { "false" } else { "true" }
    $env:LANTERN_DISCORD_ENABLE_MENTIONS = if ($EnableMentions) { "true" } else { "false" }

    Write-Host "Starting Lantern Discord bot."
    Write-Host "Endpoint: $Endpoint$ChatPath"
    Write-Host "Replies: $(if ($PublicReplies) { 'public' } else { 'ephemeral' })"
    Write-Host "Mentions: $(if ($EnableMentions) { 'enabled' } else { 'disabled' })"
    Write-Host "Boundary: token loaded for this process only; keep this window open while the bot is online."

    python -m lantern.discord_bot
}
finally {
    $env:DISCORD_BOT_TOKEN = $null
    $plainToken = $null
    Pop-Location
}
