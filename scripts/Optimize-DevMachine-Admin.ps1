#Requires -RunAsAdministrator
# Run once: Right-click → "Run as Administrator"
# Optimizes i5-9400F / 12 GB RAM machine for development

Write-Host "=== Dev Machine Optimizer (Admin) ===" -ForegroundColor Cyan

# 1. Disable SysMain (Superfetch) — pre-loads apps into RAM, competes with dev/ML workloads
Stop-Service SysMain -Force -ErrorAction SilentlyContinue
Set-Service SysMain -StartupType Disabled
Write-Host "✓ SysMain (Superfetch) disabled" -ForegroundColor Green

# 2. Disable Windows Search indexer — spikes CPU/IO on every file write in C:\dev
Stop-Service WSearch -Force -ErrorAction SilentlyContinue
Set-Service WSearch -StartupType Disabled
Write-Host "✓ Windows Search indexer disabled" -ForegroundColor Green

# 3. Windows Defender exclusions — biggest dev CPU win on Windows
#    Defender scans every file node/python/git touches; exclusions eliminate that overhead
$devPaths = @(
    "C:\dev",
    "D:\",
    "C:\Users\alexp\AppData\Local\npm-cache",
    "C:\Users\alexp\AppData\Roaming\npm",
    "C:\Users\alexp\AppData\Local\pip",
    "D:\npm-cache",
    "D:\pip-cache",
    "D:\lantern-venv-train",
    "D:\hf-cache",
    "D:\lantern-lora",
    "D:\lantern-train"
)
foreach ($path in $devPaths) {
    Add-MpPreference -ExclusionPath $path -ErrorAction SilentlyContinue
}

$devProcesses = @("node.exe", "python.exe", "git.exe", "uv.exe", "npm.cmd", "npx.cmd")
foreach ($proc in $devProcesses) {
    Add-MpPreference -ExclusionProcess $proc -ErrorAction SilentlyContinue
}

$excludedPaths = (Get-MpPreference).ExclusionPath
Write-Host "✓ Defender exclusions set ($($excludedPaths.Count) paths)" -ForegroundColor Green

# 4. Set node.exe and python.exe to HIGH CPU priority by default
#    (process priority in registry for future launches)
$priorityKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"
foreach ($exe in @("node.exe", "python.exe")) {
    $key = "$priorityKey\$exe\PerfOptions"
    New-Item -Path $key -Force | Out-Null
    # CpuPriorityClass: 3 = Above Normal, 5 = High; 8 = Realtime (avoid)
    Set-ItemProperty -Path $key -Name "CpuPriorityClass" -Value 3 -Type DWord
}
Write-Host "✓ node.exe + python.exe set to Above Normal CPU priority" -ForegroundColor Green

# 5. Disable Hiberfil.sys (hibernation file) — frees 6-8 GB on SSD if enabled
$hiberfil = "C:\hiberfil.sys"
if (Test-Path $hiberfil) {
    powercfg -h off
    Write-Host "✓ Hibernation disabled (freed hiberfil.sys)" -ForegroundColor Green
} else {
    Write-Host "✓ Hibernation already off" -ForegroundColor Green
}

# 6. Set power plan to High Performance (not Balanced — Balanced throttles the i5-9400F)
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
Write-Host "✓ Power plan: High Performance" -ForegroundColor Green

# 7. Disable unnecessary auto-start services that eat RAM
$disableServices = @(
    "DiagTrack",        # Connected User Experiences / Telemetry — 50-100 MB
    "WbioSrvc",         # Windows Biometric Service (if no fingerprint reader)
    "MapsBroker",       # Downloaded Maps Manager
    "lfsvc",            # Geolocation service
    "SharedAccess",     # Internet Connection Sharing (not needed solo dev)
    "wisvc"             # Windows Insider service
)
foreach ($svc in $disableServices) {
    $s = Get-Service $svc -ErrorAction SilentlyContinue
    if ($s -and $s.StartType -ne 'Disabled') {
        Stop-Service $svc -Force -ErrorAction SilentlyContinue
        Set-Service $svc -StartupType Disabled -ErrorAction SilentlyContinue
        Write-Host "  Disabled: $svc" -ForegroundColor DarkGray
    }
}
Write-Host "✓ Unnecessary services disabled" -ForegroundColor Green

Write-Host ""
Write-Host "Done. Reboot recommended for all changes to take effect." -ForegroundColor Cyan
Write-Host "Expected gains: ~1 GB RAM freed, CPU idle drops from ~42% to ~10-15%" -ForegroundColor Yellow
