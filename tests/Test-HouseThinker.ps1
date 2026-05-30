param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path $Root).Path
$script = Join-Path $repoRoot "scripts\Invoke-HouseThinker.ps1"
if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
    throw "Missing Invoke-HouseThinker.ps1"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("house-thinker-test-{0}" -f ([guid]::NewGuid()))
New-Item -ItemType Directory -Force -Path `
    (Join-Path $tempRoot "data\rag-house"), `
    (Join-Path $tempRoot "data\world-model"), `
    (Join-Path $tempRoot "reports"), `
    (Join-Path $tempRoot "manifests") | Out-Null

try {
    @{
        generatedAt = "2026-05-29T00:00:00Z"
        sources = @(@{ name = "lantern-os" })
        ragRecordCount = 2
        recentRagRecords = @(@{ topic = "claim"; claim = "test claim" })
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $tempRoot "data\rag-house\flat-rag-house-latest.json") -Encoding UTF8

    '{"timestamp":"2026-05-29T00:00:00Z","claim":"test claim","prior":0.5,"posterior":0.7,"decision":"candidate"}' |
        Set-Content -LiteralPath (Join-Path $tempRoot "data\world-model\belief-ledger.jsonl") -Encoding UTF8

    "# Patent Test`n`n| LC-001 | patent_candidate | claim evidence |" |
        Set-Content -LiteralPath (Join-Path $tempRoot "reports\NOVEL-WORKSTREAM-PATENT-TEST.md") -Encoding UTF8

    "# Convergence Test`n`nagent convergence proof gate" |
        Set-Content -LiteralPath (Join-Path $tempRoot "manifests\CONVERGENCE-TEST.md") -Encoding UTF8

    $resultJson = & powershell -NoProfile -ExecutionPolicy Bypass -File $script -Root $tempRoot -Once
    $result = ($resultJson | Out-String).Trim() | ConvertFrom-Json
    if (-not $result.ok) { throw "House thinker result was not ok" }
    if ($result.neuralNet -ne $false) { throw "House thinker must not claim neuralNet=true" }
    if ($result.counts.patentEvidenceMatches -lt 1) { throw "Expected patent evidence match" }
    if ($result.counts.convergenceEvidenceMatches -lt 1) { throw "Expected convergence evidence match" }
    if ($result.method.binarySort -notmatch "safe/fun") { throw "Expected safe/fun method in validation output" }

    foreach ($relative in @(
        "data\house-thinker\thought-ledger.jsonl",
        "data\house-thinker\patent-claim-candidates.jsonl",
        "data\house-thinker\agent-convergence-candidates.jsonl",
        "manifests\validation\HOUSE-THINKER-LATEST.json"
    )) {
        $path = Join-Path $tempRoot $relative
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing output $relative" }
    }

    $patentLine = Get-Content -LiteralPath (Join-Path $tempRoot "data\house-thinker\patent-claim-candidates.jsonl") -First 1 | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace([string]$patentLine.bucket)) { throw "Expected patent candidate safe/fun bucket" }

    Write-Host "House thinker test passed."
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
