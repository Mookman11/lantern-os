param(
    [string]$ZipPath = "c:\Users\alexp\OneDrive\Desktop\imagesandreports.zip",
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$IngestLabel = "imagesandreports-2026-06-02",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# ── Paths ──────────────────────────────────────────────────────────────────────
$extractDir     = Join-Path $Root "data\ingest\$IngestLabel"
$imagesOut      = Join-Path $Root "data\images\caadi"
$reportsOut     = Join-Path $Root "data\reports\caadi"
$seedsOut       = Join-Path $Root "rag\seeds"
$seedFile       = Join-Path $seedsOut "caad-ingest-$IngestLabel.md"
$manifestFile   = Join-Path $Root "manifests\evidence\caad-ingest-$IngestLabel.json"

# Ensure directories
if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $imagesOut, $reportsOut, $seedsOut | Out-Null
}

# ── Extract if needed ──────────────────────────────────────────────────────────
$extractedDir = Join-Path $extractDir "imagesandreports"
if (-not (Test-Path $extractedDir)) {
    Write-Host "[EXTRACT] $ZipPath -> $extractDir" -ForegroundColor Cyan
    if (-not $DryRun) {
        Expand-Archive -Path $ZipPath -DestinationPath $extractDir -Force
    }
}

# ── Ingestion tracking ─────────────────────────────────────────────────────────
$pdfList  = [System.Collections.Generic.List[object]]::new()
$imgList  = [System.Collections.Generic.List[object]]::new()
$htmlList = [System.Collections.Generic.List[object]]::new()

# ── Scan extracted contents ────────────────────────────────────────────────────
$files = Get-ChildItem -Path $extractedDir -File -Recurse

foreach ($file in $files) {
    $rel = $file.FullName.Substring($extractedDir.Length).TrimStart("\")
    switch ($file.Extension.ToLower()) {
        ".pdf" {
            $pdfList.Add([pscustomobject]@{
                name     = $file.Name
                relPath  = $rel
                fullPath = $file.FullName
                bytes    = $file.Length
            })
        }
        ".png" {
            $imgList.Add([pscustomobject]@{
                name     = $file.Name
                relPath  = $rel
                fullPath = $file.FullName
                bytes    = $file.Length
            })
        }
        ".html" {
            $htmlList.Add([pscustomobject]@{
                name     = $file.Name
                relPath  = $rel
                fullPath = $file.FullName
                bytes    = $file.Length
            })
        }
    }
}

Write-Host "[SCAN] PDFs: $($pdfList.Count), Images: $($imgList.Count), HTML: $($htmlList.Count)" -ForegroundColor Gray

# ── PDF metadata extraction (Python/pypdf) ─────────────────────────────────────
$pythonScript = @"
import json, sys, os
from pathlib import Path
try:
    from pypdf import PdfReader
except ImportError:
    print(json.dumps({"error": "pypdf not installed"}))
    sys.exit(1)

results = []
for path in sys.argv[1:]:
    try:
        reader = PdfReader(path)
        meta = reader.metadata or {}
        pages = len(reader.pages)
        text_preview = ""
        try:
            for page in reader.pages[:3]:
                text_preview += page.extract_text() or ""
                if len(text_preview) > 1200:
                    break
        except Exception:
            pass
        text_preview = text_preview[:1200].strip().replace("\n", " ")
        results.append({
            "filename": Path(path).name,
            "pages": pages,
            "title": str(meta.get("/Title", "") or ""),
            "author": str(meta.get("/Author", "") or ""),
            "subject": str(meta.get("/Subject", "") or ""),
            "creator": str(meta.get("/Creator", "") or ""),
            "producer": str(meta.get("/Producer", "") or ""),
            "text_preview": text_preview
        })
    except Exception as e:
        results.append({"filename": Path(path).name, "error": str(e)})

print(json.dumps(results, indent=2))
"@

$pdfPaths = $pdfList | ForEach-Object { $_.fullPath }
$pdfMetaJson = ""
if ($pdfPaths.Count -gt 0) {
    $tempPy = [System.IO.Path]::GetTempFileName() + ".py"
    Set-Content -Path $tempPy -Value $pythonScript -Encoding UTF8
    $pdfMetaJson = python $tempPy @pdfPaths
    Remove-Item $tempPy -ErrorAction SilentlyContinue
}

$pdfMeta = @()
try { $pdfMeta = $pdfMetaJson | ConvertFrom-Json } catch {}

# ── Copy images ────────────────────────────────────────────────────────────────
$copiedImages = [System.Collections.Generic.List[object]]::new()
foreach ($img in $imgList) {
    $dest = Join-Path $imagesOut $img.name
    if (-not $DryRun) {
        Copy-Item -Path $img.fullPath -Destination $dest -Force
    }
    $imgSha = "dryrun"
    if (-not $DryRun) {
        $imgSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $dest).Hash.ToLowerInvariant()
    }
    $copiedImages.Add([pscustomobject]@{
        name   = $img.name
        bytes  = $img.bytes
        sha256 = $imgSha
    })
}

# ── Copy PDFs ──────────────────────────────────────────────────────────────────
$copiedPdfs = [System.Collections.Generic.List[object]]::new()
foreach ($pdf in $pdfList) {
    $dest = Join-Path $reportsOut $pdf.name
    if (-not $DryRun) {
        Copy-Item -Path $pdf.fullPath -Destination $dest -Force
    }
    $pdfSha = "dryrun"
    if (-not $DryRun) {
        $pdfSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $dest).Hash.ToLowerInvariant()
    }
    $meta = $pdfMeta | Where-Object { $_.filename -eq $pdf.name } | Select-Object -First 1
    $mPages = 0; $mTitle = ""; $mAuthor = ""; $mSubject = ""; $mPreview = ""; $mError = ""
    if ($meta) {
        $mPages = $meta.pages
        $mTitle = $meta.title
        $mAuthor = $meta.author
        $mSubject = $meta.subject
        $mPreview = $meta.text_preview
        $mError = $meta.error
    }
    $copiedPdfs.Add([pscustomobject]@{
        name         = $pdf.name
        bytes        = $pdf.bytes
        sha256       = $pdfSha
        pages        = $mPages
        title        = $mTitle
        author       = $mAuthor
        subject      = $mSubject
        text_preview = $mPreview
        error        = $mError
    })
}

# ── Build CAAD seed markdown ───────────────────────────────────────────────────
$stamp = (Get-Date).ToString("o")
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("# CAAD Ingest — $IngestLabel") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("Date: $stamp") | Out-Null
$lines.Add("Status: RAG seed / archive-ingest") | Out-Null
$lines.Add("Scope: Batch ingestion of images and reports from operator zip archive") | Out-Null
$lines.Add("Boundary: Catalog only. Full text extraction deferred to operator review.") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("## Archive Summary") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("| Type | Count | Total Bytes |") | Out-Null
$lines.Add("|------|-------|-------------|") | Out-Null
$totalPdfBytes = ($pdfList | Measure-Object -Property bytes -Sum).Sum
$totalImgBytes = ($imgList | Measure-Object -Property bytes -Sum).Sum
$totalHtmlBytes = ($htmlList | Measure-Object -Property bytes -Sum).Sum
$lines.Add("| PDFs | $($pdfList.Count) | $totalPdfBytes |") | Out-Null
$lines.Add("| Images | $($imgList.Count) | $totalImgBytes |") | Out-Null
$lines.Add("| HTML | $($htmlList.Count) | $totalHtmlBytes |") | Out-Null
$lines.Add("| **Total** | **$($files.Count)** | **$($totalPdfBytes + $totalImgBytes + $totalHtmlBytes)** |") | Out-Null
$lines.Add("") | Out-Null

# PDF table
$lines.Add("## PDF Reports") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("| File | Pages | Title | Author | Subject | Bytes | SHA256 |") | Out-Null
$lines.Add("|------|-------|-------|--------|---------|-------|--------|") | Out-Null
foreach ($p in $copiedPdfs) {
    $titleEsc = ($p.title -replace "\|", "\\|" -replace "\n", " ")
    $authorEsc = ($p.author -replace "\|", "\\|" -replace "\n", " ")
    $subjectEsc = ($p.subject -replace "\|", "\\|" -replace "\n", " ")
    $lines.Add("| $($p.name) | $($p.pages) | $titleEsc | $authorEsc | $subjectEsc | $($p.bytes) | $($p.sha256) |") | Out-Null
}
$lines.Add("") | Out-Null

# Image table
$lines.Add("## Images") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("| File | Bytes | SHA256 |") | Out-Null
$lines.Add("|------|-------|--------|") | Out-Null
foreach ($img in $copiedImages) {
    $lines.Add("| $($img.name) | $($img.bytes) | $($img.sha256) |") | Out-Null
}
$lines.Add("") | Out-Null

# Text previews for PDFs with extractable content
$lines.Add("## Extracted Previews (first 1200 chars)") | Out-Null
$lines.Add("") | Out-Null
foreach ($p in $copiedPdfs | Where-Object { $_.text_preview -and $_.text_preview.Length -gt 50 }) {
    $lines.Add("### $($p.name)") | Out-Null
    $lines.Add("") | Out-Null
    $lines.Add("````text") | Out-Null
    $lines.Add($p.text_preview) | Out-Null
    $lines.Add("````") | Out-Null
    $lines.Add("") | Out-Null
}

# Errors
$errors = $copiedPdfs | Where-Object { $_.error }
if ($errors.Count -gt 0) {
    $lines.Add("## Extraction Errors") | Out-Null
    $lines.Add("") | Out-Null
    foreach ($e in $errors) {
        $lines.Add("- $($e.name): $($e.error)") | Out-Null
    }
    $lines.Add("") | Out-Null
}

# Storage locations
$lines.Add("## Storage Locations") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("- PDFs: `data/reports/caadi/`") | Out-Null
$lines.Add("- Images: `data/images/caadi/`") | Out-Null
$lines.Add("- Seed: `rag/seeds/$(Split-Path $seedFile -Leaf)`") | Out-Null
$lines.Add("") | Out-Null

$lines.Add("## Next Steps") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("1. Review extracted previews for relevance") | Out-Null
$lines.Add("2. Promote high-value PDFs to full-text RAG seeds via `rag_local_knowledge_base.py`") | Out-Null
$lines.Add("3. Tag images for use in surfaces/dashboards") | Out-Null
$lines.Add("4. Run `Update-InternalHouseRag.ps1` to re-index") | Out-Null
$lines.Add("") | Out-Null

# Write seed
if (-not $DryRun) {
    $lines | Set-Content -LiteralPath $seedFile -Encoding UTF8
}

# ── Manifest ───────────────────────────────────────────────────────────────────
$manifest = [ordered]@{
    schema       = "lantern.caad_ingest.v1"
    generatedAt  = $stamp
    label        = $IngestLabel
    sourceZip    = $ZipPath
    dryRun       = [bool]$DryRun.IsPresent
    counts       = [ordered]@{
        pdfs  = $pdfList.Count
        images = $imgList.Count
        html   = $htmlList.Count
    }
    bytes        = [ordered]@{
        pdfs  = $totalPdfBytes
        images = $totalImgBytes
        html   = $totalHtmlBytes
    }
    seedFile     = $seedFile
    imagesDir    = $imagesOut
    reportsDir   = $reportsOut
    pdfs         = @($copiedPdfs | ForEach-Object {
        [ordered]@{
            name   = $_.name
            bytes  = $_.bytes
            sha256 = $_.sha256
            pages  = $_.pages
            title  = $_.title
            author = $_.author
        }
    })
    images       = @($copiedImages | ForEach-Object {
        [ordered]@{
            name   = $_.name
            bytes  = $_.bytes
            sha256 = $_.sha256
        }
    })
}

if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path (Split-Path $manifestFile -Parent) | Out-Null
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestFile -Encoding UTF8
}

# ── Summary ────────────────────────────────────────────────────────────────────
Write-Host "`n=== CAAD Ingest Summary ===" -ForegroundColor Cyan
Write-Host "Label      : $IngestLabel"
Write-Host "PDFs       : $($pdfList.Count) ($totalPdfBytes bytes)"
Write-Host "Images     : $($imgList.Count) ($totalImgBytes bytes)"
Write-Host "HTML       : $($htmlList.Count) ($totalHtmlBytes bytes)"
Write-Host "Seed file  : $seedFile"
Write-Host "Manifest   : $manifestFile"
Write-Host "Images dir : $imagesOut"
Write-Host "Reports dir: $reportsOut"
if ($DryRun) { Write-Host "[DRY RUN — no files written]" -ForegroundColor Yellow }
else { Write-Host "[DONE]" -ForegroundColor Green }

exit 0
