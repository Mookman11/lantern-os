# Keystone Next Chat Handoff

Status: next-window handoff marker.

Last reviewed: 2026-05-09.

Use this file to resume Alex's HFF/Keystone convergence work from repo state
instead of relying on chat continuity alone.

## Start here

```text
repo: human-flourishing-frameworks/human-flourishing-frameworks
local checkout Alex used: C:\tmp\human-flourishing-frameworks-scan
validated public URL: https://human-flourishing-frameworks.onrender.com
```

## Current checkpoint

```text
Render public smoke check passed from Alex's local machine.
Exit code was 0.
Nodes endpoint returned [] twice.
Docs-only convergence material has been landed on master.
PR #20 remains open/draft and should not be merged without explicit review.
```

## Read these docs first

```text
docs/keystone-public-copy-incident-memory.md
docs/release-smoke-evidence-protocol.md
docs/keystone-top-risk-mitigation-sprint.md
docs/keystone-anomaly-and-tail-risk-model.md
docs/convergence-status.md
docs/keystone-memory-contract.md
docs/capability-confidence-model.md
```

## Commands to rerun

From cmd.exe:

```bat
git pull
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate_public_site.ps1 -BaseUrl "https://human-flourishing-frameworks.onrender.com"
echo %ERRORLEVEL%
scripts\check_nodes_api.cmd https://human-flourishing-frameworks.onrender.com
```

## Rules for the next window

```text
Inspect before acting.
Do not confuse Render with Railway.
Do not confuse cmd.exe with PowerShell.
Do not claim live state without fresh evidence.
Do not commit raw chat logs.
Keep PR #20 held until reviewed.
Prefer small docs/tests/scripts commits.
```

## Short goal

```text
Reach a defensible checkpoint quickly:
1. confirm repo head;
2. confirm public smoke still passes;
3. classify why nodes are empty;
4. keep high-risk work held;
5. record evidence before making claims.
```
