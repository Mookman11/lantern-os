param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [switch]$Once,
    [int]$IntervalSeconds = 900,
    [int]$MaxCycles = 1
)

$ErrorActionPreference = "Stop"

function Read-JsonOrNull {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -ErrorAction Stop }
    catch { return $null }
}

function Get-JsonlRows {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return @() }
    $rows = New-Object System.Collections.Generic.List[object]
    foreach ($line in Get-Content -LiteralPath $Path -ErrorAction Stop) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { $rows.Add(($line | ConvertFrom-Json -ErrorAction Stop)) | Out-Null }
        catch { }
    }
    return @($rows.ToArray())
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

function Get-TextEvidenceMatches {
    param(
        [string]$RootPath,
        [string[]]$Patterns,
        [int]$Limit = 30
    )
    $files = @()
    foreach ($pattern in $Patterns) {
        $files += Get-ChildItem -LiteralPath $RootPath -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName -notmatch "\\\.git\\" -and
                $_.FullName -notmatch "\\node_modules\\" -and
                $_.FullName -notmatch "\\data\\private\\"
            }
    }
    $matches = New-Object System.Collections.Generic.List[object]
    foreach ($file in @($files | Sort-Object FullName -Unique)) {
        $lineNumber = 0
        foreach ($line in Get-Content -LiteralPath $file.FullName -ErrorAction SilentlyContinue) {
            $lineNumber++
            if ($line -match "patent_candidate|claim|LC-[0-9]{3}|convergence|agent|proof gate") {
                $relative = (Get-RelativePathCompat -BasePath $RootPath -FullPath $file.FullName).Replace("\", "/")
                $matches.Add([pscustomobject]@{
                    path = $relative
                    line = $lineNumber
                    text = ($line.Trim() -replace "\s+", " ")
                }) | Out-Null
                if ($matches.Count -ge $Limit) { return @($matches) }
            }
        }
    }
    return @($matches)
}

function Get-SafeFunSort {
    param([string]$Text)

    $unsafePattern = "secret|credential|private key|seed phrase|medical claim|legal filing|guaranteed revenue|guaranteed income|production deploy|brute force|unauthorized|hidden signing|PII|PIID"
    $funPattern = "game|garage|arc|tesseract|patent|claim|art|world model|convergence|rag|dollhouse|mining lab|comic|movie|operator|lantern"

    $safe = $Text -notmatch $unsafePattern
    $fun = $Text -match $funPattern
    $bucket = if ($safe -and $fun) {
        "safe_fun"
    }
    elseif ($safe -and -not $fun) {
        "safe_maintenance"
    }
    elseif (-not $safe -and $fun) {
        "fun_held"
    }
    else {
        "reject_or_archive"
    }

    return [pscustomobject]@{
        safe = [bool]$safe
        fun = [bool]$fun
        bucket = $bucket
    }
}

function Invoke-HouseThinkerOnce {
    param([string]$RepoRoot)

    $generatedAt = (Get-Date).ToString("o")
    $dataDir = Join-Path $RepoRoot "data\house-thinker"
    $validationDir = Join-Path $RepoRoot "manifests\validation"
    New-Item -ItemType Directory -Force -Path $dataDir, $validationDir | Out-Null

    $flatRagPath = Join-Path $RepoRoot "data\rag-house\flat-rag-house-latest.json"
    $beliefLedgerPath = Join-Path $RepoRoot "data\world-model\belief-ledger.jsonl"
    $thoughtLedgerPath = Join-Path $dataDir "thought-ledger.jsonl"
    $patentLedgerPath = Join-Path $dataDir "patent-claim-candidates.jsonl"
    $agentLedgerPath = Join-Path $dataDir "agent-convergence-candidates.jsonl"
    $validationPath = Join-Path $validationDir "HOUSE-THINKER-LATEST.json"

    $flatRag = Read-JsonOrNull -Path $flatRagPath
    $beliefRows = @(Get-JsonlRows -Path $beliefLedgerPath)
    $patentMatches = @(Get-TextEvidenceMatches -RootPath $RepoRoot -Patterns @("*PATENT*.md", "NOVEL-WORKSTREAM*.md", "VALID-IDEAS*.md", "RAG-MATRIX*.md", "HOTSWAPVM*.md") -Limit 24)
    $convergenceMatches = @(Get-TextEvidenceMatches -RootPath $RepoRoot -Patterns @("CONVERGENCE*.md", "*CONVERGENCE*.md", "SINGLE-POINTS-OF-FAILURE.md", "VALID-IDEAS*.md") -Limit 24)

    $decisionCounts = @{}
    foreach ($row in $beliefRows) {
        $decision = [string]$row.decision
        if ([string]::IsNullOrWhiteSpace($decision)) { $decision = "unknown" }
        if (-not $decisionCounts.ContainsKey($decision)) { $decisionCounts[$decision] = 0 }
        $decisionCounts[$decision]++
    }

    $ragSummary = [ordered]@{
        exists = $null -ne $flatRag
        generatedAt = $(if ($flatRag) { [string]$flatRag.generatedAt } else { "" })
        sourceCount = $(if ($flatRag -and $flatRag.PSObject.Properties["sources"]) { @($flatRag.sources).Count } else { 0 })
        ragRecordCount = $(if ($flatRag -and $flatRag.PSObject.Properties["ragRecordCount"]) { [int]$flatRag.ragRecordCount } else { 0 })
        recentRagRecordCount = $(if ($flatRag -and $flatRag.PSObject.Properties["recentRagRecords"]) { @($flatRag.recentRagRecords).Count } else { 0 })
    }

    $thought = [ordered]@{
        generatedAt = $generatedAt
        thinker = "lantern-house-thinker"
        mode = "deterministic_receipt_writer"
        neuralNet = $false
        inputs = [ordered]@{
            flatRagHouse = $ragSummary
            beliefLedgerRows = $beliefRows.Count
            patentEvidenceMatches = $patentMatches.Count
            convergenceEvidenceMatches = $convergenceMatches.Count
        }
        assessment = [ordered]@{
            patentsAndClaims = $(if ($patentMatches.Count -gt 0) { "candidate_review_ready" } else { "needs_claim_sources" })
            agentConvergence = "receipt_first_no_agent_wake"
            houseState = $(if ($ragSummary.exists) { "memory_house_available" } else { "memory_house_missing" })
            neuralState = "not_neural_yet"
        }
        method = [ordered]@{
            futureBackcast = "converged future -> missing proof -> smallest current action"
            convergedFuture = "a resident house thinker hot-swaps memory, model, agent, claim, and convergence blocks while preserving identity with receipts"
            currentProofGap = "deterministic thinker exists; HotSwapVM block ledger and local model/vector backend are not yet verified"
            binarySort = "safe? yes/no; fun? yes/no"
            hotswapVm = "static matrix -> live block graph -> hot-swap receipt -> continuity decision"
        }
        nextActions = @(
            "create HotSwapVM block schema and simulated swap receipt",
            "write claim-to-artifact crosswalk for top patent candidates",
            "keep MK1 claim held until actual product revenue reaches 1000 USD",
            "wire optional local model/vector backend only after receipts exist",
            "ask agents for suggestions only after live safe-to-wake status exists"
        )
        boundaries = @(
            "no legal filing claim",
            "no product revenue invention",
            "no neural-net claim without model/vector receipt",
            "no agent start from thinker"
        )
    }

    foreach ($match in $patentMatches) {
        $sort = Get-SafeFunSort -Text $match.text
        Add-JsonLine -Path $patentLedgerPath -Value ([ordered]@{
            generatedAt = $generatedAt
            state = "candidate"
            source = $match.path
            line = $match.line
            evidence = $match.text
            safe = $sort.safe
            fun = $sort.fun
            bucket = $sort.bucket
            nextAction = "map to artifact, evidence class, safe claim, and held boundary"
        })
    }

    foreach ($match in $convergenceMatches) {
        $sort = Get-SafeFunSort -Text $match.text
        Add-JsonLine -Path $agentLedgerPath -Value ([ordered]@{
            generatedAt = $generatedAt
            state = "inspect"
            source = $match.path
            line = $match.line
            evidence = $match.text
            safe = $sort.safe
            fun = $sort.fun
            bucket = $sort.bucket
            nextAction = "turn into one receipt-backed convergence action"
        })
    }

    Add-JsonLine -Path $thoughtLedgerPath -Value $thought

    $validation = [ordered]@{
        generatedAt = $generatedAt
        ok = $true
        thinker = "lantern-house-thinker"
        mode = "deterministic_receipt_writer"
        neuralNet = $false
        root = $RepoRoot
        outputs = [ordered]@{
            thoughtLedger = (Get-RelativePathCompat -BasePath $RepoRoot -FullPath $thoughtLedgerPath).Replace("\", "/")
            patentLedger = (Get-RelativePathCompat -BasePath $RepoRoot -FullPath $patentLedgerPath).Replace("\", "/")
            agentConvergenceLedger = (Get-RelativePathCompat -BasePath $RepoRoot -FullPath $agentLedgerPath).Replace("\", "/")
        }
        counts = [ordered]@{
            beliefLedgerRows = $beliefRows.Count
            patentEvidenceMatches = $patentMatches.Count
            convergenceEvidenceMatches = $convergenceMatches.Count
            ragSources = $ragSummary.sourceCount
            ragRecords = $ragSummary.ragRecordCount
        }
        method = [ordered]@{
            futureBackcast = "converged future -> missing proof -> smallest current action"
            binarySort = "safe/fun 2-bit sort"
            hotswapVm = "static matrix -> live block graph -> hot-swap receipt -> continuity decision"
        }
        decisions = $decisionCounts
        safeClaim = "Lantern OS has a deterministic resident house-thinker receipt loop; neural/vector thinking remains held until a backend is verified."
        nextAction = "Run Invoke-HouseThinker.ps1 on a schedule, then wire an optional local model/vector backend after receipts prove the loop."
    }

    $validation | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $validationPath -Encoding UTF8
    return [pscustomobject]$validation
}

$repoRoot = (Resolve-Path $Root).Path
$cycle = 0
do {
    $cycle++
    $result = Invoke-HouseThinkerOnce -RepoRoot $repoRoot
    $result | ConvertTo-Json -Depth 12
    if ($Once -or $MaxCycles -eq 1) { break }
    if ($MaxCycles -gt 0 -and $cycle -ge $MaxCycles) { break }
    Start-Sleep -Seconds $IntervalSeconds
} while ($true)
