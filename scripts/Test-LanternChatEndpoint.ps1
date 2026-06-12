#Requires -Version 5.0
<#
.SYNOPSIS
    Tests whether the Lantern Chat local server endpoint is reachable.

.DESCRIPTION
    Sends an HTTP GET request to the Lantern Chat endpoint (default:
    http://127.0.0.1:4177) with a 3-second timeout. Reports the URL tested,
    the HTTP status code (or the error reason), and a PASS/FAIL verdict.

    Exit codes:
        0  - Server responded with HTTP 200-299 (PASS)
        1  - Connection refused, timeout, or non-2xx response (FAIL)

.PARAMETER Url
    The endpoint URL to test. Defaults to http://127.0.0.1:4177

.EXAMPLE
    .\Test-LanternChatEndpoint.ps1

.EXAMPLE
    .\Test-LanternChatEndpoint.ps1 -Url 'http://127.0.0.1:4177'

.NOTES
    Compatible with Windows PowerShell 5.0+
    Does NOT require administrator privileges.
#>
[CmdletBinding()]
param(
    [string]$Url = 'http://127.0.0.1:4177'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'SilentlyContinue'

Write-Host "Lantern Chat Endpoint Test"
Write-Host "--------------------------"
Write-Host "URL tested : $Url"

$timeoutSeconds = 3
$statusCode     = $null
$errorReason    = $null
$pass           = $false

try {
    # Use HttpWebRequest for fine-grained timeout control (PS 5 compatible)
    $request                = [System.Net.HttpWebRequest]::Create($Url)
    $request.Method         = 'GET'
    $request.Timeout        = $timeoutSeconds * 1000   # milliseconds
    $request.ReadWriteTimeout = $timeoutSeconds * 1000
    $request.AllowAutoRedirect = $true

    $response   = $request.GetResponse()
    $statusCode = [int]$response.StatusCode
    $response.Close()

    if ($statusCode -ge 200 -and $statusCode -lt 300) {
        $pass = $true
    } else {
        $errorReason = "Non-success HTTP status"
    }
}
catch [System.Net.WebException] {
    $webEx = $_.Exception
    if ($webEx.Response -ne $null) {
        $statusCode  = [int]$webEx.Response.StatusCode
        $errorReason = "HTTP error: $($webEx.Response.StatusDescription)"
    } elseif ($webEx.Status -eq [System.Net.WebExceptionStatus]::Timeout) {
        $errorReason = "Timeout after ${timeoutSeconds}s"
    } elseif ($webEx.Status -eq [System.Net.WebExceptionStatus]::ConnectFailure) {
        $errorReason = "Connection refused (server may not be running)"
    } else {
        $errorReason = "Network error: $($webEx.Status)"
    }
}
catch {
    $errorReason = "Unexpected error: $_"
}

# Report status code or reason
if ($statusCode -ne $null) {
    Write-Host "HTTP status : $statusCode"
} else {
    Write-Host "HTTP status : N/A"
}

if ($errorReason) {
    Write-Host "Reason     : $errorReason"
}

if ($pass) {
    Write-Host "Result     : PASS"
    exit 0
} else {
    Write-Host "Result     : FAIL"
    exit 1
}
