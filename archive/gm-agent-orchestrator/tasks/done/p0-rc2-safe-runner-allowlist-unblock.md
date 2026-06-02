# P0 RC2 Safe Runner Allowlist Unblock

role_owner: gpt  
fallback_owner: codex  
risk_class: high  
budget_class: light  
terminal_rule: done|failed|requeued|blocked

## Objective

Unblock RC2 contract tasks by enabling the minimal safe execution surface required for bounded validation and repo-state checks.

## Blocker Context

Previous RC2 task `p0-rc2-message-ingress-contract.md` failed because:

- safe runner rejected argument array handling for `["-Root","."]`,
- required validation scripts were not allowlisted,
- required `git status --short` evidence path was unavailable from exposed tool surface.

## Required Changes

1. Safe runner argument handling:
   - accept JSON array argument payloads for script args (for example `["-Root","."]`).

2. Safe runner allowlist additions:
   - `git status --short` (read-only repo state check),
   - `tests\\Test-OrchestratorStatusJson.ps1`,
   - `tests\\Test-OrchMcpServerContracts.ps1`.

3. Preserve guardrails:
   - no arbitrary shell execution exposure,
   - no destructive git operations,
   - no broad wildcard allowlisting.

## Validation Commands

```powershell
git status --short
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-OrchMcpSafePowerShellToolContract.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-OrchMcpServerContracts.ps1 -Root .
```

MCP smoke (through exposed tool path):

- run_safe_powershell with `Get-OrchestratorStatus.ps1` using JSON-array args,
- run_safe_powershell with `Test-OrchestratorStatusJson.ps1` using JSON-array args.

## Evidence Required

- before/after behavior for argument-array handling,
- before/after allowlist behavior for both validation scripts,
- command/tool outputs showing pass/fail,
- one next action.

## Terminal Criteria

- `done`: minimal allowlist + argument handling fixed and validated.
- `failed|blocked`: fix incomplete or validation failing with first blocker recorded.
- `requeued`: partial fix with explicit remaining gap and safe retry step.
