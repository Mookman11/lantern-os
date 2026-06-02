# Make Lantern webcam eye glow blue

Priority: P0
Owner: claude
Created: 2026-05-14T16:42:28Z
Source: connector-action

## Objective
Implement the non-negotiable Lantern webcam visual rule: Lantern's eye glows blue on the webcam-facing surface.

## Requirement
- Lantern eye color: blue.
- This is not optional.
- The blue glow must be visible in the webcam-facing Lantern surface or preview.
- If there are multiple Lantern faces or eyes, the primary active eye state must glow blue.

## Scope
1. Find the current Lantern UI, webcam, preview, avatar, overlay, or broadcast surface entry point.
2. If a real UI entry point exists, implement the blue glowing eye there.
3. If no safe implementation entry point exists, create the design/spec artifact `lantern/space-convergence-theme.md` and include the blue webcam eye as a hard requirement.
4. Preserve the space convergence direction: Lantern, Courtney, gauges, friends, Discord, desktop app, home PC.

## Safety and privacy
- Do not silently enable camera access.
- Do not record video.
- Do not stream video.
- Do not access webcam without explicit local operator consent.
- Implementation may define a webcam-facing preview or overlay, but live camera use must remain opt-in.

## Validation
- Show files inspected.
- Show files changed.
- Show `git status --short` before and after.
- Provide proof that the final UI/spec says: Lantern eye glows blue on webcam.
- Stop after one useful artifact or one failed validation cycle.

## Do not
- Do not delete, reset, clean, force-push, or merge master.
- Do not claim the missing HFF anchor URL was loaded.
- Do not trade money or hide money.
- Do not start device control beyond a safe preview/spec.
