# Task: Fix MCP dispatch headless null-safe guard (#256)

Priority: P0
Owner: claude or codex
Estimated time: 30 min
Depends on: PR #277 merged (CI green)
Blocks: all 5 agent slots dispatching via MCP

## Context

Issue #256. All 5 slots fail when `start_agent` or `rerun_agent` is called
without the optional `headless` argument. The MCP server runs under
`Set-StrictMode -Version Latest`, which throws when accessing a property
that doesn't exist on the input object.

Reported error: `"property headless cannot be found"`  -  raised in
`scripts/Start-OrchMcpServer.ps1` around line 175 (tool dispatch handler
for `start_agent` / `rerun_agent`).

## Scope

- `scripts/Start-OrchMcpServer.ps1`  -  add null-safe guard before accessing
  `headless` and `dry_run` optional params in the tool argument handlers.
- No changes to public tool schema. Optional args stay optional.
- Pattern: `$headless = if ($Arguments.PSObject.Properties['headless']) { [bool]$Arguments.headless } else { $false }`

## Done criteria

- MCP call to `start_agent` with no `headless` argument returns a valid
  tool result (not a StrictMode property error).
- Existing tests pass: `tests/Test-OrchMcpServerContracts.ps1`,
  `tests/Test-OrchMcpOpsToolsContract.ps1`.
- Branch pushed, PR open against master.

## Verify

```powershell
# Parser check first
powershell -NoProfile -Command "
  [System.Management.Automation.Language.Parser]::ParseFile(
    'scripts\Start-OrchMcpServer.ps1', [ref]`$null, [ref]`$errs)
  `$errs | ForEach-Object { Write-Error `$_ }
"

# Targeted test
pwsh -NoProfile -ExecutionPolicy Bypass -File tests\Test-OrchMcpOpsToolsContract.ps1
```

## Reference

- Issue: #256
- Mentioned in RC3 tracker: #259 Phase 1.1
