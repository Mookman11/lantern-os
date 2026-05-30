param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$OldBlockId = "matrixex-static-rag-matrix",
    [string]$NewBlockId = "hotswapvm-continuity-ship",
    [string]$OperatorIntent = "local-first evidence-gated Lantern OS control plane",
    [string]$IdentityAnchor = "lantern-os repo lineage plus append-only receipts",
    [string]$RollbackPlan = "restore previous block id and mark attempted swap as fork_or_hold"
)

$ErrorActionPreference = "Stop"

function Get-StringHash {
    param([Parameter(Mandatory = $true)][string]$Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        $hash = $sha.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Add-JsonLine {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    $dir = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    ($Value | ConvertTo-Json -Depth 12 -Compress) | Add-Content -LiteralPath $Path -Encoding UTF8
}

function Get-RelativePathCompat {
    param(
        [Parameter(Mandatory = $true)][string]$BasePath,
        [Parameter(Mandatory = $true)][string]$FullPath
    )
    $base = (Resolve-Path -LiteralPath $BasePath).Path.TrimEnd("\", "/")
    $full = (Resolve-Path -LiteralPath $FullPath).Path
    $baseUri = [System.Uri]::new($base + [System.IO.Path]::DirectorySeparatorChar)
    $fullUri = [System.Uri]::new($full)
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($fullUri).ToString()).Replace("/", "\")
}

$repoRoot = (Resolve-Path $Root).Path
$generatedAt = (Get-Date).ToString("o")
$dataDir = Join-Path $repoRoot "data\hotswapvm"
$validationDir = Join-Path $repoRoot "manifests\validation"
New-Item -ItemType Directory -Force -Path $dataDir, $validationDir | Out-Null

$oldPayload = "old block: static MatrixEx/RAG matrix concept; risk: fake queue if it cannot swap while running"
$newPayload = "new block: HotSwapVM continuity concept; blocks slide out and in while identity is proven by receipts"

$oldBlock = [ordered]@{
    generatedAt = $generatedAt
    blockId = $OldBlockId
    blockType = "concept"
    state = "outgoing"
    payloadHash = Get-StringHash -Value $oldPayload
    summary = $oldPayload
}

$newBlock = [ordered]@{
    generatedAt = $generatedAt
    blockId = $NewBlockId
    blockType = "concept"
    state = "incoming"
    payloadHash = Get-StringHash -Value $newPayload
    summary = $newPayload
}

$anchors = [ordered]@{
    operatorIntent = $OperatorIntent
    identityAnchor = $IdentityAnchor
    repoLineage = "current working tree root: $repoRoot"
    blockLineage = "$OldBlockId -> $NewBlockId"
    rollbackPlan = $RollbackPlan
}

$sameShip = -not [string]::IsNullOrWhiteSpace($OperatorIntent) -and
    -not [string]::IsNullOrWhiteSpace($IdentityAnchor) -and
    -not [string]::IsNullOrWhiteSpace($RollbackPlan) -and
    ($oldBlock.payloadHash -ne $newBlock.payloadHash)

$swap = [ordered]@{
    generatedAt = $generatedAt
    swapId = "hsvm-{0}" -f (Get-StringHash -Value "$generatedAt|$OldBlockId|$NewBlockId").Substring(0, 16)
    mode = "simulated_live_receipt_no_runtime_mutation"
    oldBlockId = $OldBlockId
    newBlockId = $NewBlockId
    oldPayloadHash = $oldBlock.payloadHash
    newPayloadHash = $newBlock.payloadHash
    continuityAnchors = $anchors
    sameShip = [bool]$sameShip
    decision = $(if ($sameShip) { "same_ship" } else { "fork_or_hold" })
    boundary = "patent candidate receipt only; not a filed patent, legal opinion, production hot-swap claim, or novelty claim"
}

$blocksPath = Join-Path $dataDir "blocks.jsonl"
$swapPath = Join-Path $dataDir "swap-ledger.jsonl"
$validationPath = Join-Path $validationDir "HOTSWAPVM-LATEST.json"

Add-JsonLine -Path $blocksPath -Value $oldBlock
Add-JsonLine -Path $blocksPath -Value $newBlock
Add-JsonLine -Path $swapPath -Value $swap

$validation = [ordered]@{
    generatedAt = $generatedAt
    ok = $true
    system = "hotswapvm"
    decision = $swap.decision
    sameShip = $swap.sameShip
    outputs = [ordered]@{
        blocks = (Get-RelativePathCompat -BasePath $repoRoot -FullPath $blocksPath).Replace("\", "/")
        swapLedger = (Get-RelativePathCompat -BasePath $repoRoot -FullPath $swapPath).Replace("\", "/")
    }
    proof = [ordered]@{
        oldBlockId = $OldBlockId
        newBlockId = $NewBlockId
        oldPayloadHash = $oldBlock.payloadHash
        newPayloadHash = $newBlock.payloadHash
        blockLineage = $anchors.blockLineage
        rollbackPlan = $RollbackPlan
    }
    safeClaim = "HotSwapVM has a deterministic simulated swap receipt. Runtime hot-swap remains held until code modules are swapped under test."
}

$validation | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $validationPath -Encoding UTF8
[pscustomobject]$validation | ConvertTo-Json -Depth 12
