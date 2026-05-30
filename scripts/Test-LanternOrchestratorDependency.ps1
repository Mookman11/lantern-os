param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $OutputPath) {
    $OutputPath = Join-Path $Root "manifests\validation\LANTERN-ORCHESTRATOR-DEPENDENCY-LATEST.json"
}

$manifestPath = Join-Path $Root "manifests\orchestrator-dependency.json"
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Missing orchestrator dependency manifest: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$healthOk = $false
$toolCount = 0
$toolNames = @()
$agentStatus = $null
$queueCounts = $null
$errors = New-Object System.Collections.Generic.List[string]

function Invoke-McpJsonRpc {
    param(
        [string]$Url,
        [string]$Method,
        [object]$Params = @{},
        [int]$TimeoutSec = 20
    )

    $body = @{
        jsonrpc = "2.0"
        id = [guid]::NewGuid().ToString("N")
        method = $Method
        params = $Params
    } | ConvertTo-Json -Depth 12

    return Invoke-RestMethod -Uri $Url -Method Post -ContentType "application/json" -Body $body -TimeoutSec $TimeoutSec
}

function Get-ToolTextJson {
    param([object]$RpcResult)
    $text = $RpcResult.result.content |
        Where-Object { $_.type -eq "text" } |
        Select-Object -First 1 -ExpandProperty text
    if ([string]::IsNullOrWhiteSpace($text)) { return $null }
    return $text | ConvertFrom-Json
}

try {
    $health = Invoke-RestMethod -Uri $manifest.mcp.healthUrl -Method Get -TimeoutSec 8
    $healthOk = $health.ok -eq $true
}
catch {
    $errors.Add("health_failed: $($_.Exception.Message)") | Out-Null
}

try {
    $toolsResult = Invoke-McpJsonRpc -Url $manifest.mcp.rpcUrl -Method "tools/list"
    $toolNames = @($toolsResult.result.tools | ForEach-Object { [string]$_.name })
    $toolCount = $toolNames.Count
}
catch {
    $errors.Add("tools_list_failed: $($_.Exception.Message)") | Out-Null
}

try {
    $agentStatus = Get-ToolTextJson (Invoke-McpJsonRpc -Url $manifest.mcp.rpcUrl -Method "tools/call" -Params @{
        name = "get_agent_status"
        arguments = @{}
    })
}
catch {
    $errors.Add("agent_status_failed: $($_.Exception.Message)") | Out-Null
}

try {
    $queue = Get-ToolTextJson (Invoke-McpJsonRpc -Url $manifest.mcp.rpcUrl -Method "tools/call" -Params @{
        name = "get_queue_summary"
        arguments = @{}
    })
    $queueCounts = $queue.counts
}
catch {
    $errors.Add("queue_summary_failed: $($_.Exception.Message)") | Out-Null
}

$requiredReadTools = @($manifest.requiredReadTools)
$missingReadTools = @($requiredReadTools | Where-Object { $toolNames -notcontains $_ })
$heldMutationToolsVisible = @($manifest.requiredMutationToolsHeldBehindApproval | Where-Object { $toolNames -contains $_ })
$agents = @($agentStatus.agents)
$availableAgents = @($agentStatus.availableAgents)
$activeAgents = @($agents | Where-Object { $_.currentTask })
$staleAgents = @($agents | Where-Object { $_.state -eq "stale" })

$status = if (-not $healthOk -or $missingReadTools.Count -gt 0) {
    "dependency_offline_or_incomplete"
}
elseif ($availableAgents.Count -eq 0 -and $activeAgents.Count -eq 0) {
    "mcp_ready_fleet_rebuild_required"
}
else {
    "mcp_ready_fleet_partially_runnable"
}

$result = [ordered]@{
    generatedAt = (Get-Date).ToString("o")
    manifestPath = $manifestPath
    outputPath = $OutputPath
    dependencyId = $manifest.dependencyId
    repoPath = $manifest.repoPath
    repoExists = Test-Path -LiteralPath $manifest.repoPath
    mcp = [ordered]@{
        healthUrl = $manifest.mcp.healthUrl
        rpcUrl = $manifest.mcp.rpcUrl
        healthOk = $healthOk
        toolCount = $toolCount
        missingReadTools = $missingReadTools
        heldMutationToolsVisible = $heldMutationToolsVisible
    }
    fleet = [ordered]@{
        status = $status
        configuredAgentCount = $agents.Count
        availableAgentCount = $availableAgents.Count
        activeAgentCount = $activeAgents.Count
        staleAgentCount = $staleAgents.Count
        queue = $queueCounts.queue
        active = $queueCounts.active
        done = $queueCounts.done
        failed = $queueCounts.failed
        headline = $agentStatus.headline
        nextHumanAction = $agentStatus.availability.nextHumanAction
    }
    targetLanternSlots = $manifest.targetLanternSlots
    boundary = [ordered]@{
        dependencyMode = $manifest.lanternPolicy.dependencyMode
        staleSlotsAreRunnable = $false
        canUseReadTools = ($healthOk -and $missingReadTools.Count -eq 0)
        canDispatchAgents = $false
        reason = "Agent dispatch requires fresh slot preflight, clean worktree evidence, and explicit human approval."
    }
    errors = $errors
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null
$result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$result | ConvertTo-Json -Depth 12
