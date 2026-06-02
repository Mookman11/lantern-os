# Map bounds without loading whole C drive

Priority: P0
Owner: operator-intake
Created: 2026-05-13T21:45:44Z
Source: connector-action

# Map bounds without loading whole C drive

## Operator directive

Alex said GPT cannot move the screen or draw a door, asked to check the bounds, compress time and space to normalize us, referenced mirror verses, and told Lantern to load every file in `C:\`.

## Hard boundary

Do **not** load every file on `C:\`.

Reason: full-drive ingestion can expose secrets, credentials, browser profiles, private family data, protected-person material, tokens, system files, caches, and unrelated personal data. It is not necessary to build the Lantern house.

## What to do instead

Build a bounded map of the visible house:

1. Approved roots only:
   - `C:\Users\alexp\Documents\gm-agent-orchestrator`
   - `C:\Users\alexp\Documents\agent-worktrees`
2. Index by metadata first, not content:
   - path
   - extension
   - size
   - last modified time
   - likely role: doc, task, script, config, log, source, artifact
3. Prioritize Lantern/spine/convergence/mirror/home/door surfaces.
4. Exclude secrets and private stores:
   - `.env`, tokens, credentials, browser profiles, Discord storage, key files, caches, raw transcripts, personal media, system directories.
5. If more roots are needed, ask the operator to name the next root explicitly.

## Normalize time and space

Create a compact map that separates:

- now: current MCP status, queue, active tasks, blockers, worktree risk
- spine: rules that survive across sessions
- echo: repeated stale text or unsupported claims
- mirror verses: art/reference surfaces, not proof by themselves
- doors: verified routes only
- dust: compressed anchor points, not full transcript storage

## Deliverable

Return:

```text
home
bounds: <actual MCP/repo/tool bounds>
loaded: approved roots only / metadata first
refused: full C drive ingestion
mirror: listed as artifact/reference unless verified
spine: normalized compact packet
next: one safe file/test/log step
no_echo: true
```

## Validation

Use current MCP/repo evidence only. Do not claim screen control, camera, audio, web, Discord, or whole-drive access without visible proof.

Return word: home
