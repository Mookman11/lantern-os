# Fix Test-GeminiCliPreflightContract LASTEXITCODE leak

Priority: P1
Owner: gemini
Created: 2026-05-06T08:46:51Z
Source: connector-action

# Fix: Remove LASTEXITCODE reset that masks child exit code

## Goal
In `tests/Test-GeminiCliPreflightContract.ps1`, remove the 4-line block that resets
`$global:LASTEXITCODE = 0` after the child preflight runs. This reset masks the child
process exit code and can hide failures.

## File
`tests/Test-GeminiCliPreflightContract.ps1`

## What to change
Find and remove these lines (around line 47-50):
```
    # The child preflight is expected to exit 1 for a blocked MCP state. Keep that
    # assertion, but do not let the expected child exit code poison this parent
    # contract test's final process exit code after validations pass.
    $global:LASTEXITCODE = 0
```

The `$exitCode` variable already captures the child's exit code from `$LASTEXITCODE`
on the line above. The global reset is unnecessary and masks failures.

## Done criteria
- The 4-line block is removed
- The test still validates `$exitCode -eq 0` produces a throw
- Changed file passes PowerShell parser check
- Committed and pushed with a PR opened

## Guardrails
- Do not modify other test files
- Do not change the test logic or assertions
- Keep the existing exit-code validation flow intact
