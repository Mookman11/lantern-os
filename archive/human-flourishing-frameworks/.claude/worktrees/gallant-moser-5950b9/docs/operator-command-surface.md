# Operator Command Surface

## Purpose

The operator normally interacts with local Windows repos through Command Prompt (`cmd.exe`), not raw PowerShell. Operator-facing commands should default to CMD syntax unless PowerShell is explicitly requested or wrapped.

## Correction

Lantern previously gave commands such as `Test-Path` and `ls` as if the operator were in PowerShell. The operator's live logs showed Command Prompt behavior:

```text
'Test-Path' is not recognized as an internal or external command
'ls' is not recognized as an internal or external command
```

## Default Rule

```text
For operator-facing Windows commands, assume cmd.exe by default.
Use `dir`, `type`, `cd /d`, `where`, and `python -m unittest` patterns.
Only use PowerShell through explicit `powershell -NoProfile -ExecutionPolicy Bypass -Command "..."` wrappers.
```

## CMD Equivalents

| Intent | CMD default | PowerShell only if wrapped |
|---|---|---|
| change drive/path | `cd /d C:\path` | `Set-Location C:\path` |
| list files | `dir` | `Get-ChildItem` |
| print file | `type file.txt` | `Get-Content file.txt` |
| test path | `if exist path echo exists` | `Test-Path path` |
| find text | `findstr text file` | `Select-String text file` |
| run tests without pytest | `python -m unittest ...` | same |

## Sensor / Memory Optimization

This command-surface fact is a high-signal operator preference and should be loaded as a small operational anchor, not rediscovered from large markdown context every time.

```text
operator_command_shell = cmd.exe
operator_local_hff_repo = C:\tmp\hff-master-clean
operator_orchestrator_repo = C:\Users\alexp\Documents\gm-agent-orchestrator
```

## Validation Phrase

```text
Convergence requires tracking small high-signal facts across turns. Defaulting to PowerShell after repeated CMD evidence is sensor drift.
```
