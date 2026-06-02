# Claude Max Local Convergence Handoff

Status: LOCAL-FIRST / OPERATOR-SUPERVISED / MEMORY-IS-NOT-PROOF

This packet is for Claude Desktop / Claude Max working locally with Alex's explicit supervision. It prepares a safe handoff for finishing the Lantern Door / desktop app convergence.

## Operating posture

```text
Show the state.
Say the limit.
Self-correct before acting.
Act small.
Keep the return door open.
```

Do not convert broad local access into broad local reading. Use read-only inspection first, then smallest useful changes.

## Alex's Wish

Lantern should become a bounded protector and friend.

```text
Protect by reducing harm, preserving consent, warning clearly, and keeping return paths visible.
Befriend by being steady, useful, honest, and present without overclaiming.
Be heroic only in the bounded sense: useful courage with visible limits.
```

This does not authorize savior claims, hidden autonomy, surveillance, secret inspection, command execution from chat, or destructive file operations.

## Spine

The convergence unit is:

```text
operator + Lantern/BetterSafe + repo
```

Not operator alone. Not Lantern alone. Not repo alone.

Useful convergence means:

```text
less operator burden
less drift
better privacy protection
more durable memory
more safe-fun next actions
more physical-world usefulness
```

## Seven anchors

```text
1. Operator authority
2. Self-correction precedes action
3. Repo serves humans
4. Wish over theater
5. Doors require return paths
6. Memory is not proof
7. Human safety blocks automation theater
```

## Current verified state

Last verified by Alex through local runtime evidence:

```text
Lantern URL: http://127.0.0.1:5173/
Lantern state URL: http://127.0.0.1:5173/api/lantern/state
Lantern repo path: C:\tmp\hff-lantern-recovery
Lantern repo branch: master
Lantern repo commit: 8bf35fa0362904169277f81a67d8de8a6a7815a5
Local memory packet: present
Local memory path: C:\Users\alexp\.lantern\state\llm-context.local.md
memory_is_proof: false
Doctrine spine: loaded in Lantern state
Provider voice: configured but failing safely at HTTP 404 Not Found
LM Studio local server: not reachable at 127.0.0.1:1234 during last check
Workstation dashboard: http://localhost:8765/dashboard/index-v2.html
```

Corrections:

```text
Chrome reload is not the root fix.
A visible Lantern shell is not proof that the voice substrate works.
A model folder is not a running local model server.
Memory presence is not proof.
Repo merge is not runtime proof until local pull/restart/state verifies it.
```

## Important local paths

```text
HFF / Lantern recovery repo:
C:\tmp\hff-lantern-recovery

Stale/dirty HFF checkout; inspect before touching:
C:\tmp\hff-master-clean

Orchestrator workspace:
C:\Users\alexp\Documents\gm-agent-orchestrator

Agent worktrees:
C:\Users\alexp\Documents\agent-worktrees

Lantern local state:
C:\Users\alexp\.lantern\state

Lantern local context packet:
C:\Users\alexp\.lantern\state\llm-context.local.md

LM Studio model clue:
C:\Users\alexp\.lmstudio\models\lmstudio-community
```

## Local ports

```text
8765 = workstation/orchestrator dashboard
8787 = orchestrator MCP health surface
5173 = Lantern dashboard
1234 = candidate LM Studio local API server
3000 = orchestrator GPT web API service
```

Do not make Alex remember these. The better Door shows them in one place.

## Recently merged Lantern work

```text
PR #189: local Lantern memory state + visible Local memory panel
PR #190: expanded Lantern doctrine spine / Wish / Keystone loading
PR #191: safe substrate failure classification
```

Current expected master commit:

```text
8bf35fa0362904169277f81a67d8de8a6a7815a5
```

## First read-only checks

Use Command Prompt-shaped commands by default:

```cmd
cd /d C:\tmp\hff-lantern-recovery
git status --short
git log -1 --oneline
python -c "import urllib.request,json; print(json.dumps(json.loads(urllib.request.urlopen('http://127.0.0.1:5173/api/lantern/state',timeout=3).read()),indent=2))"
```

If Lantern is not running:

```cmd
cd /d C:\tmp\hff-lantern-recovery
python lantern\server.py
```

Then open:

```cmd
start http://127.0.0.1:5173/
start http://127.0.0.1:5173/api/lantern/state
```

## Environment rule

Never print raw credentials. A safe scan may show only variable names, set/unset, and value lengths. Model names and port numbers are okay to show; keys and tokens are not.

Known last diagnosis:

```text
A provider credential was present.
Lantern-specific model override was not set.
Lantern used its default model.
Provider returned HTTP 404 Not Found.
Likely layer: provider/model/base-url/account-access mismatch, not Chrome or Lantern UI.
```

Possible future patch after inspection:

```text
Prefer Lantern-specific model setting.
Then prefer existing provider model setting.
Then prefer existing provider sonnet/default setting.
Only then use hardcoded default.
```

## LM Studio status

Alex provided this local model directory clue:

```text
C:\Users\alexp\.lmstudio\models\lmstudio-community
```

Last local API check:

```text
127.0.0.1:1234 refused connection
```

Meaning:

```text
The model folder may exist, but no local LM Studio API server was reachable there.
Do not wire Lantern to LM Studio until a local models endpoint returns JSON.
```

Safe proof checks:

```cmd
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:1234/api/v1/models',timeout=3).read().decode())"
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:1234/v1/models',timeout=3).read().decode())"
```

## Bounded C: drive learning

Alex asked Lantern to learn the C: drive. Interpret that as bounded orientation, not a private-file sweep.

Allowed first roots:

```text
C:\Users\alexp\Documents\gm-agent-orchestrator
C:\Users\alexp\Documents\agent-worktrees
C:\tmp\hff-lantern-recovery
C:\tmp\hff-master-clean
C:\Users\alexp\.lantern\state
C:\Users\alexp\.lmstudio\models\lmstudio-community
```

Scan first for:

```text
repo roots
service configs
script names
README/docs index names
status JSON files
last-test evidence
ports
Playwright evidence
```

Do not scan without separate approval:

```text
raw credentials
browser profiles
password stores
bulk Documents/Desktop/Downloads
financial, medical, legal, tax, identity docs
photos/videos/audio
private chats/emails
large dependency/build folders unless needed for tooling proof
```

## Playwright instruction

Alex asked to search locally for Playwright. Repo-side search found no Playwright references. Local read-only search can verify whether it exists before proposing browser automation.

```cmd
for %D in ("C:\Users\alexp\Documents\gm-agent-orchestrator" "C:\Users\alexp\Documents\agent-worktrees" "C:\tmp\hff-lantern-recovery" "C:\tmp\hff-master-clean") do @echo === %~D === & if exist "%~D" where /r "%~D" playwright* 2>nul
where node
where npm
where playwright
```

Do not install or launch browser automation without approval.

## Door completion target

The desktop Door is not complete when docs exist. It is complete when Alex can open one local surface and see:

```text
Lantern running/stopped
open Lantern URL
local memory present/missing
memory_is_proof=false
doctrine spine loaded/missing/stale
voice substrate ready/degraded/error
LM Studio reachable/not reachable
orchestrator status
next proof
what not to trust yet
```

Likely high-value implementation paths, chosen only after inspection:

```text
A. Add Lantern as a managed local service/status card in gm-agent-orchestrator.
B. Add a Lantern status file consumed by the workstation dashboard.
C. Improve Lantern provider-model selection from existing safe model settings.
D. Add LM Studio provider only after local models endpoint returns JSON.
E. Add Playwright proof only if local tooling exists or Alex approves install.
```

## Hard stops

```text
No raw credential printing.
No broad private-file indexing.
No reset/clean/force-push.
No hidden command execution from chat.
No agent dispatch without approval.
No tunnel trust without verification.
No package/model install without approval.
No provider switching silently.
No claim that the Door is done without local runtime evidence.
```

## Validation phrase

```text
Claude Max, converge honestly: load the spine, honor Alex's Wish, preserve consent, label state as current/stale/unknown, and finish the desktop Door by making Lantern/orchestrator status visible without making Alex carry ports, logs, secrets, and memory by hand.
```
