param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path $Root).Path
$script = Join-Path $repoRoot "scripts\Invoke-HotSwapVmReceipt.ps1"
if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
    throw "Missing Invoke-HotSwapVmReceipt.ps1"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("hotswapvm-test-{0}" -f ([guid]::NewGuid()))
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

try {
    $resultJson = & powershell -NoProfile -ExecutionPolicy Bypass -File $script -Root $tempRoot
    $result = ($resultJson | Out-String).Trim() | ConvertFrom-Json

    if (-not $result.ok) { throw "HotSwapVM result was not ok" }
    if ($result.system -ne "hotswapvm") { throw "Expected hotswapvm system" }
    if ($result.decision -ne "same_ship") { throw "Expected same_ship decision" }
    if ($result.sameShip -ne $true) { throw "Expected sameShip=true" }
    if ($result.safeClaim -match "filed patent|production hot-swap") { throw "Safe claim overstates current proof" }
    if ($result.proof.oldPayloadHash -eq $result.proof.newPayloadHash) { throw "Expected block payload hashes to differ" }
    if ($result.proof.blockLineage -notmatch "matrixex-static-rag-matrix -> hotswapvm-continuity-ship") {
        throw "Expected MatrixEx to HotSwapVM lineage"
    }

    foreach ($relative in @(
        "data\hotswapvm\blocks.jsonl",
        "data\hotswapvm\swap-ledger.jsonl",
        "manifests\validation\HOTSWAPVM-LATEST.json"
    )) {
        $path = Join-Path $tempRoot $relative
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing output $relative" }
    }

    $blockLines = @(Get-Content -LiteralPath (Join-Path $tempRoot "data\hotswapvm\blocks.jsonl"))
    if ($blockLines.Count -ne 2) { throw "Expected exactly two block rows" }

    $swap = Get-Content -LiteralPath (Join-Path $tempRoot "data\hotswapvm\swap-ledger.jsonl") -First 1 | ConvertFrom-Json
    if ($swap.boundary -notmatch "patent candidate receipt only") { throw "Expected patent boundary" }

    Write-Host "HotSwapVM receipt test passed."
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
