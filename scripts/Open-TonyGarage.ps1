$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$garage = Join-Path $root "surfaces\tony-garage\index.html"

if (-not (Test-Path $garage)) {
    throw "Tony Garage surface not found at $garage"
}

Start-Process -FilePath $garage
Write-Output $garage
