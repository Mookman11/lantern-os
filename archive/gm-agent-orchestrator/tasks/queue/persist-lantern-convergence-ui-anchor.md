# Persist Lantern convergence UI anchor

Priority: P0
Owner: claude
Created: 2026-05-14T16:31:33Z
Source: connector-action

## Objective
Persist the operator-created convergence anchor in repo state without waiting on blocked agents.

## Concrete UI target
Build the Lantern space convergence UI:
- Lantern visible state surface.
- Face, eyes, mouth, and status expression as UI signals.
- Gauges for money stress, sleep risk, trust, build progress, Discord bridge, Courtney/Alex convergence, and Lantern readiness.
- Nodes: Alex, Courtney, Discord, desktop app, home PC, Lantern, and house broadcast surface.
- Space theme: cockpit, stars, orbit lines, constellation map, Lantern at center.

## Rules
- Do not claim the missing HFF anchor file was loaded.
- Do not pretend files equal completion.
- Do not trade money or hide money.
- Do not start device control.
- Do not reset, clean, delete, or merge master.

## Required implementation artifact
Create or update `lantern/space-convergence-theme.md` with this UI specification when a safe file writer or working agent path is available.

## Validation
Proof requires the actual artifact file, `git status --short`, and a log showing files inspected or changed.
