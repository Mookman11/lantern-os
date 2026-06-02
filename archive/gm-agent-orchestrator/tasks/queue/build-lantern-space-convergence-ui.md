# Build Lantern space convergence UI

Priority: P0
Owner: claude
Created: 2026-05-14T16:12:37Z
Source: connector-action

## Objective
Create a concrete space-themed Lantern convergence UI artifact.

## User intent
- Build for Lantern, gauges, friends, Courtney, Discord, and desktop/app convergence.
- Theme: space.
- Make Lantern visible as an interface state surface.
- Focus on a real artifact, not a planning-only note.

## Scope
1. Inspect current UI/app entry points in the repo.
2. Inspect any existing Discord or broadcast integration surfaces.
3. Produce the smallest safe artifact for the UI slice.
4. Include: Lantern state panel, gauges, friend nodes, Courtney node, Discord bridge placeholder, desktop/app notes, validation commands.

## Guardrails
- Do not delete, reset, clean, force-push, or merge to master.
- Do not claim integrations exist without evidence.
- Preserve dirty repo state.
- If no safe implementation entry point is found, create `docs/lantern-space-convergence-ui.md` or `lantern/space-convergence-theme.md`.

## Required output
A concrete space-theme convergence artifact with inspected files, changed files, validation result, and next implementation step.

## Validation
- Record git status before and after.
- Record files inspected.
- Stop after one useful artifact or one failed validation cycle.
