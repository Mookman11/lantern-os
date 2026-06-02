#Requires -Version 5.0
<#
.SYNOPSIS
    Creates a desktop shortcut and Start Menu shortcut pointing to the Lantern Chat local server.

.DESCRIPTION
    Creates a .url shortcut on the current user's Desktop and in the Start Menu
    (Programs folder) for the Lantern Chat web interface. No admin rights, no IDE,
    no external dependencies required.

.PARAMETER TargetUrl
    The URL the shortcut should open. Defaults to http://127.0.0.1:4177

.EXAMPLE
    .\New-LanternChatShortcut.ps1

.EXAMPLE
    .\New-LanternChatShortcut.ps1 -TargetUrl 'http://127.0.0.1:4177'

.NOTES
    Compatible with Windows PowerShell 5.0+
    Does NOT require administrator privileges.
    Does NOT require Windsurf or any IDE.
#>
[CmdletBinding()]
param(
    [string]$TargetUrl = 'http://127.0.0.1:4177'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-UrlShortcut {
    param(
        [string]$Path,
        [string]$Url
    )

    $content = "[InternetShortcut]`r`nURL=$Url`r`n"
    [System.IO.File]::WriteAllText($Path, $content, [System.Text.Encoding]::UTF8)
}

# --- Desktop shortcut ---
$desktopPath  = [Environment]::GetFolderPath('Desktop')
$desktopShortcut = Join-Path $desktopPath 'Lantern Chat.url'

New-UrlShortcut -Path $desktopShortcut -Url $TargetUrl

if (Test-Path $desktopShortcut) {
    Write-Host "[OK] Desktop shortcut created:"
    Write-Host "     Path : $desktopShortcut"
    Write-Host "     URL  : $TargetUrl"
} else {
    Write-Error "Failed to create desktop shortcut at '$desktopShortcut'."
}

# --- Start Menu shortcut ---
$startMenuPrograms = [Environment]::GetFolderPath('Programs')
$startMenuDir      = Join-Path $startMenuPrograms 'Lantern'

if (-not (Test-Path $startMenuDir)) {
    New-Item -ItemType Directory -Path $startMenuDir -Force | Out-Null
}

$startMenuShortcut = Join-Path $startMenuDir 'Lantern Chat.url'

New-UrlShortcut -Path $startMenuShortcut -Url $TargetUrl

if (Test-Path $startMenuShortcut) {
    Write-Host "[OK] Start Menu shortcut created:"
    Write-Host "     Path : $startMenuShortcut"
    Write-Host "     URL  : $TargetUrl"
} else {
    Write-Error "Failed to create Start Menu shortcut at '$startMenuShortcut'."
}

Write-Host ""
Write-Host "Done. Open Lantern Chat by double-clicking either shortcut or navigating to:"
Write-Host "  $TargetUrl"
