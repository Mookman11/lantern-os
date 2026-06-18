# Journal Uploads → Knowledge Center

**Date:** 2026-06-18
**Goal:** Move the research/PDF upload entry point out of the Create Dashboard and into a lightweight ChatGPT-style "+" attachment on the Journal input. Uploads flow into the Knowledge Center and a confirmation appears inline in the conversation. The ingestion pipeline was **reused, not rewritten**.

---

## Previous upload path (removed)

`create.html` had a dedicated **Research Library** card at the bottom of the Create Dashboard:

```
Create Dashboard
  └─ "Research Library" section
       └─ #pdf-upload-zone  (drop / Choose PDFs)
            └─ uploadPdfs()  →  POST /api/pdfs/upload  →  data/ingest/  →  Knowledge Center
```

This card + its `<script>` were removed from Create.

## New Journal path

`dream-chat.html` (the Journal) now has a "+" button on the **left** of the input bar:

```
[ + ]  Write something, ask a question…          [ ↑ ]
   │
   └─ click → soft popover menu:
        📄 Upload PDF          ← active
        🖼️ Upload Image  SOON
        📁 Upload File   SOON
        ✎ Paste Research SOON
        "Imported files are added to your Knowledge Center
         and become searchable throughout Lantern."
```

Flow:

```
+ → Upload PDF → file picker → POST /api/pdfs/upload (same endpoint as before)
   → data/ingest/  → Knowledge Center
   → inline confirmation bubble in the conversation:

   ┌─ KNOWLEDGE CENTER ──────────────────────────┐
   │ ✓ Uploaded research-paper.pdf               │
   │ Added to your Knowledge Center — view & search │
   └─────────────────────────────────────────────┘
```

**Scope note (decided up front):** Only **PDF** has a Knowledge Center ingestion pipeline today (`knowledgecenter.html` scans `data/ingest` for PDFs). Image / File / Paste-Research are shown but disabled with a subtle "soon" tag — no fake "added to Knowledge Center" claims, and no new ingestion pipeline was built (per the handoff's "do not rewrite the pipeline").

## Knowledge Center integration

- **Endpoint reused:** `POST /api/pdfs/upload` (`routes/pdfs.js`) — unchanged contract: multipart form field `file`, `.pdf` only, ≤100 MB, saves to `data/ingest/`, returns `{ ok, saved[], errors[] }`.
- **Indexing:** the Knowledge Center (`knowledgecenter.html` → `GET /api/pdfs`) lists everything under `data/ingest/`, so an uploaded file is immediately visible and filename-searchable there. No separate `knowledgeCenter.add()` call is needed — dropping into the ingest dir *is* the integration.
- **Reliability fix (required for "upload works"):** `routes/pdfs.js` replied on `bb.on('finish')`, which in Busboy 1.x fires **before** the file write stream flushes — so files saved to disk but the API returned `saved: []` (upload looked broken). Fixed by tracking each write as a promise and replying on `bb.on('close')` after `Promise.all(writes)`. This is a completion-timing fix in the upload handler only; PDF parsing / Knowledge Center indexing were not touched. (Also added a defensive `mkdir -p data/ingest`.)

## Files changed

| File | Change |
|---|---|
| `apps/lantern-garage/public/create.html` | Removed the **Research Library** section (HTML) and its PDF-upload `<script>`. |
| `apps/lantern-garage/public/dream-chat.html` | Added the **"+" attachment** button + popover menu + helper text (HTML), matching styles (CSS in the page `<style>`), and the upload→Knowledge-Center wiring with inline confirmation (JS). |
| `apps/lantern-garage/routes/pdfs.js` | Fixed the upload-handler write/response race so `saved[]` is accurate; defensive ingest-dir create. |

## Verification (all ✓, in-browser on the running server)

**Journal**
- "+" button visible on the left of the input bar.
- Menu opens as a soft card (Upload PDF active; Image/File/Paste = "soon").
- Real PDF driven through the input → `POST /api/pdfs/upload` succeeds.
- Confirmation bubble appears in the conversation ("✓ Uploaded … — Added to your Knowledge Center").
- No console errors.

**Knowledge Center**
- Uploaded file appears in `GET /api/pdfs` (what `knowledgecenter.html` lists) → searchable by name.
- Filename/metadata preserved (sanitized basename).

**Create**
- Research Library upload UI removed; 0 orphaned references (`pdf-upload-zone`, `uploadPdfs`, etc.); `<script>` tags balanced; page renders cleanly (upload card + projects intact).

## Future (not built — out of scope per handoff)

- Image OCR (tesseract is already a dependency) → Knowledge Center.
- Document (.docx/.txt/.md) parsing → Knowledge Center.
- "Paste Research" text → Knowledge Center note.
- Optional auto-summary of an uploaded PDF in the confirmation bubble.
- Drag-and-drop onto the Journal (currently click-to-attach only).
