# Upload Pipeline Audit — Creator Dashboard

**Date:** 2026-06-18
**Scope:** Creator Dashboard video upload flow.
**Result:** ✅ Root cause of the ~27–32% progress stall on long videos found and fixed.

---

## The pipeline (as it actually is)

```
Drop / Choose video  (create.html: handleFiles → startUpload)
        │  XHR POST /api/dreamer/upload   ← progress mapped to 8–70%
        ▼
routes/dreamer.js  "/api/dreamer/upload"
        │  busboy streams the file → data/dreamer/videos/<ts>-<name>
        │  responds { saved, file:{ path, size, ... } } on busboy 'close'
        ▼
create.html  startUpload  ← phase "Analyzing…", progress 70→90%
        │  fetch POST /api/creator-entries  { title, type, filePath }
        ▼
routes/creator-entries.js  POST
        │  creates the project entry (entryStore)
        │  generates thumbnail in the BACKGROUND (non-blocking)
        │  responds { entry } immediately
        ▼
create.html  ← progress 100% "✓ Uploaded"
        │  loadRecentEntries() → project card appears (Open / Analyze links)
        ▼
Single upload → opens /entry.html?id=…   |   Multiple → stays on dashboard
```

**Where progress is updated (client, `create.html`):**
- 8–70% — real bytes, `xhr.upload.onprogress` (loaded/total).
- 70→90% — staged when `/api/dreamer/upload` returns and project creation starts.
- 100% — when `/api/creator-entries` returns.

## Root cause of the 27–32% stall (long videos)

`routes/dreamer.js` `/api/dreamer/upload` had:

```js
const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB
file.on("data", chunk => {
  bytesUploaded += chunk.length;
  if (bytesUploaded > MAX_FILE_SIZE) {
    uploadError = new Error("File exceeds maximum size…");
    file.destroy();          // ← halts request parsing
  }
});
```

For any video over **500 MB** (i.e. most 10+ minute gameplay captures), once 500 MB had been received the handler called **`file.destroy()`**. That stops busboy from consuming the rest of the request body, so:

- the browser's upload stalls (TCP backpressure) at `≈ 500MB / totalSize` — **~27–32% for a ~1.5–1.8 GB video**,
- busboy never emits `'close'`, so **no response is ever sent**,
- the XHR hangs forever → progress frozen, project never created, user must refresh.

Every reported symptom maps to this one defect. There is **no** `Promise.race`/timeout/`AbortController` in the path, and project cards were already plain links (clickable at any status) — they simply never appeared because the upload hung before `/api/creator-entries` ran.

A secondary latent bug: the handler replied on busboy `'close'` while `fileInfo` was set in the write stream's `'finish'` handler — a race that could return `file: null` even on success.

## The fix (`routes/dreamer.js`, +45/−17)

1. **Raise the cap** to **5 GB** (env-overridable: `LANTERN_MAX_UPLOAD_MB`), so real long videos upload fully and progress reaches 100%.
2. **Never `file.destroy()` on over-limit.** Instead: `unpipe` + destroy the write stream, **delete the partial file**, and `file.resume()` to **drain** the rest of the request — so busboy emits `'close'` and a clean **`400 "File exceeds maximum size"`** is returned promptly (no hang).
3. **Wait for the write to flush before responding** (`await writePromise` in `'close'`), settling the promise on `finish` / `error` / `close` so it resolves in every path (including the destroyed-stream over-limit case). Fixes the `file: null` race too.

## Verification

| Test | Result |
|---|---|
| Normal upload (under cap), real browser path | `200`, `saved:true`, file path set, ~15 ms ✅ |
| Over-limit (2 MB vs 1 MB test cap) | `400 "File exceeds maximum size of 1MB"`, **24 ms — no hang**, partial cleaned ✅ |
| Hang check (10 s abort guard) | did **not** trip — over-limit returns promptly ✅ |

**Not verified here:** an actual 30–45 minute multi-GB upload (no such file in this environment). The fix directly removes the 500 MB boundary that caused the stall and guarantees the request always completes, but a real-world large-file run on the target machine is the final confirmation.

## Failure modes now handled

| Condition | Before | After |
|---|---|---|
| Video > 500 MB | Stall ~30%, hang forever, no project | Uploads fully (cap 5 GB) → project created |
| Video > cap | (same hang) | Prompt `400`, partial deleted, clear error in the progress row |
| Disk write error | Possible `file:null` success | `uploadError` → `400`, partial cleaned |
| busboy close/finish race | Could return `file:null` | Response waits for flush; path always populated |

## Not changed (deliberately out of scope)

The handoff also proposed a larger rebuild — create the project *before* upload (status `UPLOADING`), background-job state machine (`PROCESSING`/`ANALYZING`/`READY`/`FAILED`), checkpoint persistence + resume-on-refresh, a retry/​re-analyze/​logs UI, and a 9-stage weighted progress bar. These are **enhancements, not the bug** — the stall was entirely the cap-hang above, and project cards are already clickable at any status. They're recommended as a separate follow-up rather than bundled into this reliability fix, to avoid touching the settled UI and to keep the change reviewable. The current client progress already reflects real work (bytes → create) and no longer stalls.
