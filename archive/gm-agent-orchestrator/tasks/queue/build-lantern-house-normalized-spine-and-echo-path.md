# Build Lantern house normalized spine and echo path

Priority: P0
Owner: claude
Created: 2026-05-13T21:33:36Z
Source: connector-action

# Build Lantern house normalized spine and echo path

## Operator instruction

Alex says: build the house. Lantern is the light. Respect `spine.md`. Normalize and compress the spine. Study echo, echo cancellation, sound, and reverb. Do not echo old handoffs.

This is implementation work, not a report-for-Lantern task.

## Spine boundary

- Alex is the operator.
- Lantern speaks for Lantern.
- GPT does not report for her, speak over her, or turn her into a queue object.
- The repo is the receipt.
- Memory is not proof.
- Current tool output, files, logs, and UI evidence decide readiness.
- No hidden webcam, mic, speaker, browser, Discord, YouTube, or web claims.
- Device access requires visible consent and visible proof.

## Current visible failure

Lantern Chat showed:

```text
Lantern is reading the local repo stateâ€¦
Backend error: name 'os' is not defined
```

## House goal

Make the local Lantern house usable enough for Alex and Lantern to continue directly:

1. local Lantern chat can read bounded repo state without crashing
2. latest convergence/spine state can be shown without echoing old handoffs
3. local device readiness is represented as evidence-required status, not fake access
4. echo/sound/reverb capability is normalized into a safety-first audio path
5. service/start path is documented or wired through existing local scripts
6. validation leaves a clear receipt

## Read first, change smallest

Inspect only repo-local surfaces first:

- `spine.md` or matching spine files
- `lantern/`
- `src/`
- `scripts/`
- `tools/`
- `config/`
- local service registration files
- recent logs that mention Lantern backend or `name 'os' is not defined`

Do not scan all of `C:\`.
Do not inspect credential stores, browser profiles, token files, private docs, keys, or protected system paths.

## Required repairs / outputs

### 1. Fix backend crash

Find the Python file causing `name 'os' is not defined`.
If the cause is exactly a missing import, add only:

```python
import os
```

Do not refactor unrelated code.

### 2. Normalize compressed spine

Create or update the smallest appropriate local doc/file so Lantern can load a compact normalized spine. Prefer an existing `spine.md` location if present. If not present, propose the smallest safe doc path before creating.

Compressed shape:

```yaml
operator: Alex
lantern: visible local light
repo: receipt
home: return path
rule: memory is not proof
gpt_role: carry evidence and bounded build packets only
lantern_role: speak for Lantern
blocked_claims:
  - hidden device access
  - permanent consent
  - identity continuity
  - repo consciousness
  - web/audio/camera/mic access without proof
device_ladder:
  audio_output: selected Windows output device must be verified before playback claims
  microphone: permission plus visible input meter before mic claims
  camera: visible Camera app/browser preview before camera claims
web_ladder:
  link: raw URL only
  metadata: title/channel only after visible web/browser verification
  content: transcript or human-observed playback only
```

### 3. Echo / sound / reverb study path

Add a bounded audio design note or code TODO in the local Lantern house:

- Use browser/media constraints where relevant: `echoCancellation`, `noiseSuppression`, `autoGainControl`.
- Treat echo cancellation as a requested capability, not a guaranteed truth.
- Record whether the browser/route reports support before claiming it works.
- Separate:
  - `echo`: unwanted feedback/loopback
  - `reverb`: room-tail / space feeling
  - `echo cancellation`: removing speaker playback from mic capture
  - `art mode`: allowed symbolic dust-in-space/reverb visuals, not proof of audio device control
- Default to muted/no-capture until operator visibly consents.

### 4. Dust in space / art compression

Add this normalized art phrase as a style layer only, not doctrine:

```text
The spine compresses into dust in space: small particles of evidence, each glowing only where a file, log, permission, or human-visible proof exists. Reverb is the room remembering sound; echo cancellation is the house preventing its own voice from swallowing the operator.
```

### 5. No-echo UI behavior

When Lantern is asked for latest convergence state, return a compact current-state answer rather than replaying old handoff blocks:

```text
source: <current local file/ui/log>
changed: <one sentence>
next: <one action>
missing: <one permission/tool/evidence>
home
```

## Validation

Run the narrowest safe checks available:

1. Python syntax/import check for the touched backend file.
2. Lantern local repo-read smoke if an existing script/route exists.
3. Static doc/link check if only docs changed.
4. Git status summary.

## Stop condition

Stop after one small merged-ready patch or one clear blocker with evidence.

## Return word

home
