# Extract PR 188 camera mic listen scripts into opt-in PRs

Priority: P1
Owner: claude
Created: 2026-05-13T23:47:40Z
Source: connector-action

## Objective
Separate any webcam, microphone, Vosk, or listen-script changes from mixed PR #188 into one or more opt-in PRs.

## Guardrails
Do not merge PR #188 as-is. Do not include A/V capture in the Lantern limits-only PR. Any camera or mic work must require explicit user consent, visible opt-in, clear stop conditions, local-only behavior, and tests. No background capture. No automatic startup.

## Validation
Verify the source diff first, document privacy and consent boundaries, add targeted tests for opt-in and stop behavior, and open separate PRs only for bounded A/V pieces.
