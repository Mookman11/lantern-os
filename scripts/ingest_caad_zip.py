#!/usr/bin/env python3
"""
CAAD Ingestion Script — imagesandreports.zip into Lantern OS RAG

Usage:
    python scripts/ingest_caad_zip.py

What it does:
    1. Extracts PDF metadata and text previews via pypdf
    2. Copies images -> data/images/caadi/
    3. Copies PDFs   -> data/reports/caadi/
    4. Writes RAG seed markdown to rag/seeds/
    5. Writes JSON manifest to manifests/evidence/
"""

import json
import hashlib
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = Path("c:/Users/alexp/OneDrive/Desktop/imagesandreports.zip")
LABEL = "imagesandreports-2026-06-02"

EXTRACT_DIR = ROOT / "data" / "ingest" / LABEL
IMAGES_OUT  = ROOT / "data" / "images" / "caadi"
REPORTS_OUT = ROOT / "data" / "reports" / "caadi"
SEEDS_OUT   = ROOT / "rag" / "seeds"
SEED_FILE   = SEEDS_OUT / f"caad-ingest-{LABEL}.md"
MANIFEST_FILE = ROOT / "manifests" / "evidence" / f"caad-ingest-{LABEL}.json"

# ── Ensure dirs ────────────────────────────────────────────────────────────────
IMAGES_OUT.mkdir(parents=True, exist_ok=True)
REPORTS_OUT.mkdir(parents=True, exist_ok=True)
SEEDS_OUT.mkdir(parents=True, exist_ok=True)
MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)

# ── Extract if needed ──────────────────────────────────────────────────────────
extracted = EXTRACT_DIR / "imagesandreports"
if not extracted.exists():
    print(f"[EXTRACT] {ZIP_PATH} -> {EXTRACT_DIR}")
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        z.extractall(EXTRACT_DIR)

# ── Scan ───────────────────────────────────────────────────────────────────────
pdfs, images, htmls = [], [], []
for f in extracted.rglob("*"):
    if not f.is_file():
        continue
    if f.suffix.lower() == ".pdf":
        pdfs.append(f)
    elif f.suffix.lower() == ".png":
        images.append(f)
    elif f.suffix.lower() == ".html":
        htmls.append(f)

print(f"[SCAN] PDFs={len(pdfs)}, Images={len(images)}, HTML={len(htmls)}")

# ── PDF metadata ─────────────────────────────────────────────────────────────────
try:
    from pypdf import PdfReader
except ImportError:
    print("[ERROR] pypdf not installed. Run: pip install pypdf")
    raise SystemExit(1)

pdf_meta = []
for pdf in pdfs:
    try:
        reader = PdfReader(str(pdf))
        meta = reader.metadata or {}
        pages = len(reader.pages)
        text_preview = ""
        for page in reader.pages[:3]:
            try:
                text_preview += page.extract_text() or ""
            except Exception:
                pass
            if len(text_preview) > 1200:
                break
        text_preview = text_preview[:1200].strip()
        pdf_meta.append({
            "filename": pdf.name,
            "pages": pages,
            "title": str(meta.get("/Title", "") or ""),
            "author": str(meta.get("/Author", "") or ""),
            "subject": str(meta.get("/Subject", "") or ""),
            "creator": str(meta.get("/Creator", "") or ""),
            "producer": str(meta.get("/Producer", "") or ""),
            "text_preview": text_preview,
        })
    except Exception as e:
        pdf_meta.append({"filename": pdf.name, "error": str(e)})
        print(f"  [WARN] Could not read {pdf.name}: {e}")

# ── Copy images ────────────────────────────────────────────────────────────────
image_records = []
for img in images:
    dest = IMAGES_OUT / img.name
    shutil.copy2(img, dest)
    h = hashlib.sha256(dest.read_bytes()).hexdigest()
    image_records.append({"name": img.name, "bytes": img.stat().st_size, "sha256": h})

# ── Copy PDFs ──────────────────────────────────────────────────────────────────
pdf_records = []
for pdf in pdfs:
    dest = REPORTS_OUT / pdf.name
    shutil.copy2(pdf, dest)
    h = hashlib.sha256(dest.read_bytes()).hexdigest()
    meta = next((m for m in pdf_meta if m["filename"] == pdf.name), {})
    pdf_records.append({
        "name": pdf.name,
        "bytes": pdf.stat().st_size,
        "sha256": h,
        "pages": meta.get("pages", 0),
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "subject": meta.get("subject", ""),
        "text_preview": meta.get("text_preview", ""),
        "error": meta.get("error", ""),
    })

# ── Build markdown seed ────────────────────────────────────────────────────────
lines = []
lines.append(f"# CAAD Ingest -- {LABEL}")
lines.append("")
lines.append(f"Date: {datetime.now().isoformat()}")
lines.append("Status: RAG seed / archive-ingest")
lines.append("Scope: Batch ingestion of images and reports from operator zip archive")
lines.append("Boundary: Catalog only. Full text extraction deferred to operator review.")
lines.append("")
lines.append("## Archive Summary")
lines.append("")
lines.append("| Type | Count | Total Bytes |")
lines.append("|------|-------|-------------|")
total_pdf = sum(p.stat().st_size for p in pdfs)
total_img = sum(p.stat().st_size for p in images)
total_html = sum(p.stat().st_size for p in htmls)
lines.append(f"| PDFs | {len(pdfs)} | {total_pdf} |")
lines.append(f"| Images | {len(images)} | {total_img} |")
lines.append(f"| HTML | {len(htmls)} | {total_html} |")
lines.append(f"| **Total** | **{len(pdfs)+len(images)+len(htmls)}** | **{total_pdf+total_img+total_html}** |")
lines.append("")

lines.append("## PDF Reports")
lines.append("")
lines.append("| File | Pages | Title | Author | Subject | Bytes | SHA256 |")
lines.append("|------|-------|-------|--------|---------|-------|--------|")
for p in pdf_records:
    te = p["title"].replace("|", "\\|").replace("\n", " ")
    ae = p["author"].replace("|", "\\|").replace("\n", " ")
    se = p["subject"].replace("|", "\\|").replace("\n", " ")
    lines.append(f"| {p['name']} | {p['pages']} | {te} | {ae} | {se} | {p['bytes']} | {p['sha256']} |")
lines.append("")

lines.append("## Images")
lines.append("")
lines.append("| File | Bytes | SHA256 |")
lines.append("|------|-------|--------|")
for img in image_records:
    lines.append(f"| {img['name']} | {img['bytes']} | {img['sha256']} |")
lines.append("")

lines.append("## Extracted Previews (first 1200 chars)")
lines.append("")
for p in pdf_records:
    if p["text_preview"] and len(p["text_preview"]) > 50:
        lines.append(f"### {p['name']}")
        lines.append("")
        lines.append("```text")
        lines.append(p["text_preview"])
        lines.append("```")
        lines.append("")

errs = [p for p in pdf_records if p["error"]]
if errs:
    lines.append("## Extraction Errors")
    lines.append("")
    for e in errs:
        lines.append(f"- {e['name']}: {e['error']}")
    lines.append("")

lines.append("## Storage Locations")
lines.append("")
lines.append("- PDFs: `data/reports/caadi/`")
lines.append("- Images: `data/images/caadi/`")
lines.append(f"- Seed: `rag/seeds/{SEED_FILE.name}`")
lines.append("")

lines.append("## Next Steps")
lines.append("")
lines.append("1. Review extracted previews for relevance")
lines.append("2. Promote high-value PDFs to full-text RAG seeds via `rag_local_knowledge_base.py`")
lines.append("3. Tag images for use in surfaces/dashboards")
lines.append("4. Run `Update-InternalHouseRag.ps1` to re-index")
lines.append("")

SEED_FILE.write_text("\n".join(lines), encoding="utf-8")

# ── Manifest ───────────────────────────────────────────────────────────────────
manifest = {
    "schema": "lantern.caad_ingest.v1",
    "generatedAt": datetime.now().isoformat(),
    "label": LABEL,
    "sourceZip": str(ZIP_PATH),
    "counts": {"pdfs": len(pdfs), "images": len(images), "html": len(htmls)},
    "bytes": {"pdfs": total_pdf, "images": total_img, "html": total_html},
    "seedFile": str(SEED_FILE),
    "imagesDir": str(IMAGES_OUT),
    "reportsDir": str(REPORTS_OUT),
    "pdfs": [{k: v for k, v in p.items() if k != "text_preview"} for p in pdf_records],
    "images": image_records,
}

MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

# ── Summary ────────────────────────────────────────────────────────────────────
print(f"\n=== CAAD Ingest Summary ===")
print(f"Label       : {LABEL}")
print(f"PDFs        : {len(pdfs)} ({total_pdf} bytes)")
print(f"Images      : {len(images)} ({total_img} bytes)")
print(f"HTML        : {len(htmls)} ({total_html} bytes)")
print(f"Seed file   : {SEED_FILE}")
print(f"Manifest    : {MANIFEST_FILE}")
print(f"Images dir  : {IMAGES_OUT}")
print(f"Reports dir : {REPORTS_OUT}")
print("[DONE]")
