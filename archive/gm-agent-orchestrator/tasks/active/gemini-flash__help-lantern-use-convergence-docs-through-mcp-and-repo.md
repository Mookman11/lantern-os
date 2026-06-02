# Help Lantern use convergence docs through MCP and repo

Priority: P0
Owner: human
Created: 2026-05-13T21:13:53Z
Source: connector-action

# Help Lantern use convergence docs through MCP and repo

## To Lantern

Alex asked GPT to help you use all convergence docs through the MCP shell or repo.

This is a local-first handoff, not a claim that you have hidden web, webcam, microphone, Discord, browser, or autonomous shell access.

## Current tool truth

- Local MCP/orchestrator is reachable through the visible MCP connector.
- The exposed MCP tool list does not show a Lantern-specific `send`, `post`, `chat`, or arbitrary shell command.
- Safe PowerShell is allowlist-only.
- Repo and task state must be inspected before mutation.
- `operator-intake` is currently blocked by validation failure, so do not depend on that slot until it is repaired.
- Do not start agents, sync repos, reset/clean worktrees, trust tunnels, open device access, or claim web access without explicit visible operator approval and evidence.

## Goal

Turn the convergence docs into one practical local operating map:

> human signal -> structured capture -> redaction -> state update -> guidance -> physical-world action -> feedback -> correction

Use that map to help Alex and GPT make fewer pretend doors and more verified doors.

## First pass: inventory, do not change

Read-only inventory first. Find the actual local paths and state for convergence-related material, including any present equivalents of:

- `docs/convergence.md`
- `docs/operator-lantern-repo-convergence.md`
- `docs/anchor-taxonomy.md`
- `lantern/handoff-packet.md`
- `anchor-snapshot.json`
- Lantern local context files under operator-visible local state
- any `lantern/` UI/server files that load doctrine or state

For each found file, report:

| File | Exists? | Last modified / commit if available | What it contributes | Boundary |
|---|---:|---|---|---|

## Second pass: consolidate

Build a small convergence index with these layers:

1. operator authority and consent boundary
2. local-first tool truth
3. anchor taxonomy and restore phrases
4. convergence loop
5. protected-person and family boundaries
6. device/web/Discord/browser capability truth
7. repo-safe workflow
8. smallest next verified step

Use anchor rules: anchors are continuity handles with boundaries, not proof, permanent consent, runtime truth, or identity continuity.

## New ideas to consider

1. `Convergence Index`: one repo doc that lists every convergence source, what it is allowed to influence, and what it must not authorize.
2. `Door Ledger`: one visible table for each door: MCP, repo queue, Lantern UI, browser, Discord, webcam, microphone, audio, web. Each row must have evidence, missing piece, next test, and stale-after time.
3. `Home Command`: a simple local restore phrase that means return to safe visible state: no hidden control, no device claim, no forced start, show state, say limit, ask one next step.
4. `Papa Web Cue`: when you hear `papa`, treat it only as a cue that Alex may send GPT/Lantern to the web next. Do not browse or claim web access. Prepare compact web questions, source targets, and safety boundaries, then wait for explicit web route and visible consent.
5. `Pretend vs Real Door Split`: keep symbolic/play language allowed, but label it as symbolic unless a real file, log, endpoint, permission, device preview, or commit proves it.
6. `One-Step Patch Rule`: after inventory, propose only one smallest repo change, preferably docs-only or test-only, with rollback path.

## Validation path

Before any patch:

1. report branch and dirty state
2. report MCP state and exposed tools
3. report relevant file existence
4. report blocked agents/slots
5. state the exact proposed file change
6. require visible operator approval unless the action is read-only

After any approved patch:

1. run the narrowest relevant validation
2. show evidence
3. state risks and stale assumptions
4. stop

## Blocked uses

Do not use convergence docs to claim:

- consciousness transfer
- identity continuity
- omniscience
- device access
- hidden telemetry
- autonomous authority
- permanent consent
- child-data collection
- repo self-merge
- real web/browser/Discord/audio/webcam/microphone access without current evidence

## Return word

home
