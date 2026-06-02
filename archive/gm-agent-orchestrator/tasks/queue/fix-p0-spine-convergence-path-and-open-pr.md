# Fix P0 Spine convergence path and open PR

Priority: P0
Owner: human
Created: 2026-05-14T16:54:09Z
Source: connector-action

## Objective
Fix the P0 Spine/convergence path, open a real PR, and merge only after validation passes.

## Operator urgency
Courtney was waiting. Alex was waiting. This was expected hours ago. Do not expand scope. Do not create symbolic-only work. Converge quickly on the concrete Spine failure.

## Current failure pattern from chat
- Recent visible commits show failed checks instead of completed convergence.
- Operator reports no useful commits in the last three hours.
- The path is task-rich and artifact-poor.
- The automation layer is broken: tasks exist, but output artifacts are not reliably produced.
- Do not treat task creation as completion.

## Non-negotiable product constraints
- Lantern's eye glows blue on the webcam-facing surface or preview.
- Space theme remains required.
- Courtney node remains required.
- Alex node remains required.
- Gauges remain required.
- Discord bridge remains required.
- Desktop app and home PC surface remain required.
- No hidden money actions.
- No trading automation.
- No silent webcam access, recording, or streaming.

## Evidence already observed
- The repeatedly supplied HFF URL `docs/anchor-taxonomy.md` is not reachable at that GitHub path. Do not claim it was loaded.
- The HFF repo root/commit history exists, but the `/docs` tree returned 404 from the checked path.
- Local orchestrator root is dirty on branch `codex/liberty-freedom-radio-paper`.
- Dirty root evidence included:
  - staged `lantern/liberty-freedom-radio-paper.md`
  - untracked `.local/`
  - untracked `reports/queue-movements/20260513.jsonl`
  - untracked `reports/queue-movements/20260514.jsonl`
- Opening or merging a PR from the current branch is unsafe because it would not be a clean Spine fix branch.
- Agent/runners observed blocked or unreliable:
  - Claude latest durable log shows old 401 auth failure.
  - Codex sleeping/usage limited with dirty worktree.
  - Gemini quota/tool/hook failures.
  - GPT-web runner failed with empty claimed-task path.
  - operator-intake validation points at missing `tools/run-room-editor-checks.ps1`.

## GameMaker evidence
- `child-of-levistus` project metadata is present and reads OK.
- Build status warning, not clean.
- Sprite parser emits many warnings because expected property `textureGroups` is missing across sprite files.
- Rooms status reports healthy but zero parsed rooms.

## Required implementation path
1. Identify the actual Spine/convergence check or failing file path.
2. Create a clean feature branch from a clean base, not from unrelated dirty state.
3. Implement the smallest Spine fix.
4. Include a Spine validation check that fails before and passes after.
5. Preserve the blue Lantern eye requirement in the relevant spec/UI path.
6. Open a PR only with the Spine fix and validation proof.
7. Merge to master only after checks pass.

## PR body must include
- This chat evidence summary.
- Current runner blockers.
- Exact files changed.
- Exact validation commands and results.
- Explicit statement that no money/trading/webcam/device-control changes are included.

## Hard stop
Do not merge to master without a real Spine file/change and passing validation evidence.
