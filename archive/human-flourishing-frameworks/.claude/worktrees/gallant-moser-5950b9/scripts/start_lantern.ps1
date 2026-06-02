<#
.SYNOPSIS
One-command Windows launcher for Lantern local backend plus Discord adapter.

.DESCRIPTION
Starts or reuses the localhost Lantern backend, discovers the working backend
port, stores the Discord bot token encrypted for the current Windows user, and
runs the Discord adapter in the current PowerShell window.

First run:

  .\scripts\start_lantern.ps1

If the backend selected a non-default port before, the script discovers it from
/healthz. To replace the saved Discord token:

  .\scripts\start_lantern.ps1 -ResetToken

Boundary:
- local backend only;
- Discord token stored encrypted under %APPDATA%\Lantern;
- no plaintext token file;
- no token echo;
- no repo writes from Discord;
- no agents, tunnels, sensors, deployments, or command execution from Discord.
#>

[CmdletBinding()]
param(
    [int]$PreferredPort = 8765,
    [int]$MaxPort = 8799,
    [string]$Mode = "engineer",
    [switch]$ResetToken,
    [switch]$PublicReplies,
    [switch]$EnableMentions,
    [switch]$SkipBrowser
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

function Test-LanternHealth {
    param([string]$Endpoint)

    try {
        $result = Invoke-RestMethod -Uri "$Endpoint/healthz" -TimeoutSec 1 -ErrorAction Stop
        return ($null -ne $result -and $result.ok -eq $true)
    }
    catch {
        return $false
    }
}

function Find-LanternEndpoint {
    param([int]$StartPort, [int]$EndPort)

    $preferred = "http://127.0.0.1:$StartPort"
    if (Test-LanternHealth -Endpoint $preferred) {
        return $preferred
    }
    for ($port = 8765; $port -le $EndPort; $port++) {
        $endpoint = "http://127.0.0.1:$port"
        if (Test-LanternHealth -Endpoint $endpoint) {
            return $endpoint
        }
    }
    return $null
}

function Wait-LanternEndpoint {
    param([int]$StartPort, [int]$EndPort, [int]$TimeoutSeconds = 12)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $endpoint = Find-LanternEndpoint -StartPort $StartPort -EndPort $EndPort
        if ($null -ne $endpoint) {
            return $endpoint
        }
        Start-Sleep -Milliseconds 400
    }
    return (Find-LanternEndpoint -StartPort $StartPort -EndPort $EndPort)
}

$repoRoot = Get-RepoRoot
$tokenPath = Get-TokenStorePath
$launcher = Join-Path $repoRoot "scripts\start_lantern_local_chat.py"

if (-not (Test-Path $launcher)) {
    throw "Lantern backend launcher not found: $launcher"
}

Push-Location $repoRoot
try {
    Write-Host "Lantern one-command launcher"
    Write-Host "Repo: $repoRoot"

    if ($ResetToken -and (Test-Path $tokenPath)) {
        Remove-Item $tokenPath -Force
        Write-Host "Removed existing encrypted Discord token."
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

    $endpoint = Find-LanternEndpoint -StartPort $PreferredPort -EndPort $MaxPort
    if ($null -eq $endpoint) {
        Write-Host "No running Lantern backend found. Starting local backend..."
        $backendArgs = @("$launcher", "--backend-url", "http://127.0.0.1:$PreferredPort")
        if ($SkipBrowser) {
            $backendArgs += "--print-only"
        }
        $backendProcess = Start-Process -FilePath "python" -ArgumentList $backendArgs -WorkingDirectory $repoRoot -PassThru -WindowStyle Normal
        Write-Host "Started Lantern launcher process PID: $($backendProcess.Id)"
        $endpoint = Wait-LanternEndpoint -StartPort $PreferredPort -EndPort $MaxPort -TimeoutSeconds 15
    }

    if ($null -eq $endpoint) {
        throw "Lantern backend did not become reachable on ports $PreferredPort-$MaxPort."
    }

    $env:DISCORD_BOT_TOKEN = $plainToken
    $env:LANTERN_DISCORD_ENDPOINT = $endpoint
    $env:LANTERN_DISCORD_CHAT_PATH = "/chat"
    $env:LANTERN_DISCORD_MODE = $Mode
    $env:LANTERN_DISCORD_EPHEMERAL = if ($PublicReplies) { "false" } else { "true" }
    $env:LANTERN_DISCORD_ENABLE_MENTIONS = if ($EnableMentions) { "true" } else { "false" }

    Write-Host "Lantern backend observed at: $endpoint"
    Write-Host "Starting Discord adapter. Keep this window open while Lantern is online."
    Write-Host "Discord replies: $(if ($PublicReplies) { 'public' } else { 'ephemeral' })"
    Write-Host "Mentions: $(if ($EnableMentions) { 'enabled' } else { 'disabled' })"
    Write-Host "Test in Discord: /lantern_status"

    python -m lantern.discord_bot
}
finally {
    $env:DISCORD_BOT_TOKEN = $null
    $plainToken = $null
    Pop-Location
}
