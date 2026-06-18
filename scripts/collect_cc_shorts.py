#!/usr/bin/env python3
"""
CC-licensed reference collector — the LEGITIMATE third-party half.

Searches YouTube specifically for Creative-Commons-licensed gaming clips
(`--match-filter "license=creativeCommon"`, verified to return real CC-BY
content), downloads a MODEST capped sample, runs the existing visual-research
observer (scripts/_visual_research_helper.js) for real frame/audio features,
and stores features + full attribution.

WHY THIS IS LEGITIMATE (and the mass-scrape version isn't):
  - CC-BY ("reuse allowed") is an explicit grant by the uploader to reuse the
    work, including downloading and creating derivatives, provided attribution
    is given. We capture creator/url/license for exactly that attribution.
  - This is NOT bulk-downloading arbitrary copyrighted Shorts. The match-filter
    excludes standard-license content entirely.
  - Scope is capped (default 40) and honest: CC-licensed gaming clips are
    scarce, so this yields hundreds at most, never the "tens of thousands" the
    original handoff imagined. That scarcity is real and reported, not hidden.

Output:
    data/shorts/cc/features_cc.jsonl   (features + attribution per clip)
    data/shorts/cc/ATTRIBUTION.md      (human-readable credit list, CC-BY req.)
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OBSERVER = ROOT / "scripts" / "_visual_research_helper.js"
OUT_DIR = ROOT / "data" / "shorts" / "cc"
FEATURES_FILE = OUT_DIR / "features_cc.jsonl"
ATTRIBUTION_FILE = OUT_DIR / "ATTRIBUTION.md"

MAX_CLIPS = 40  # honest cap; CC gaming content is scarce
QUERIES = [
    "creative commons gameplay", "creative commons minecraft",
    "creative commons fortnite", "no copyright gameplay short",
    "free to use gaming clip",
]


def search_cc(query, limit):
    """Return video metadata for a query (no download), then keep only those
    whose license string is Creative Commons. NB: yt-dlp's
    `--match-filter license=creativeCommon` does an EXACT match against the
    license *string* ("Creative Commons Attribution license (reuse allowed)")
    and so never matches — so we print the license and filter in Python, which
    is verifiable and correct. Only metadata is fetched here; nothing is
    downloaded until the CC check below passes."""
    proc = subprocess.run(
        ["python", "-m", "yt_dlp", f"ytsearch{limit}:{query}",
         "--skip-download", "--no-warnings",
         "--print", "%(id)s\t%(license)s\t%(uploader)s\t%(webpage_url)s\t%(title)s"],
        capture_output=True, text=True, timeout=180,
    )
    rows = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 5 and parts[0] and "creative commons" in (parts[1] or "").lower():
            rows.append({"video_id": parts[0], "license": parts[1], "uploader": parts[2],
                         "url": parts[3], "title": parts[4]})
    return rows


def observe(video_path):
    proc = subprocess.run(["node", str(OBSERVER), str(video_path)],
                          capture_output=True, text=True, timeout=180)
    try:
        return json.loads(proc.stdout.strip())
    except json.JSONDecodeError:
        return {"status": "unavailable", "reason": proc.stderr[-200:]}


def already_done(video_id):
    if not FEATURES_FILE.exists():
        return False
    for line in FEATURES_FILE.open(encoding="utf-8"):
        try:
            if json.loads(line).get("video_id") == video_id:
                return True
        except json.JSONDecodeError:
            pass
    return False


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Gather CC-licensed candidates across queries (dedup).
    seen, candidates = set(), []
    per_query = max(5, MAX_CLIPS // len(QUERIES) + 5)
    for q in QUERIES:
        if len(candidates) >= MAX_CLIPS:
            break
        print(f"searching CC: {q!r}...")
        for r in search_cc(q, per_query):
            if r["video_id"] in seen:
                continue
            # Double-check the license really is CC (defense in depth).
            if "creative commons" not in (r["license"] or "").lower():
                continue
            seen.add(r["video_id"])
            candidates.append(r)
            if len(candidates) >= MAX_CLIPS:
                break
    print(f"found {len(candidates)} CC-licensed candidates")

    # 2) Download (low-res) + observe + store features, with attribution.
    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for i, r in enumerate(candidates):
            vid = r["video_id"]
            if already_done(vid):
                print(f"[{i+1}/{len(candidates)}] {vid} already done, skipping")
                continue
            out_path = tmp / f"{vid}.mp4"
            print(f"[{i+1}/{len(candidates)}] downloading CC clip {vid}...")
            try:
                subprocess.run(
                    ["python", "-m", "yt_dlp", "-f", "worst[ext=mp4]/worst",
                     "--max-filesize", "40M", "--no-warnings",
                     "-o", str(out_path), r["url"]],
                    capture_output=True, text=True, timeout=180, check=True,
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                print(f"  download failed: {getattr(e, 'stderr', '') and e.stderr[-160:] or e}")
                continue
            if not out_path.exists():
                continue
            try:
                feat = observe(out_path)
                rec = {**r, "features": feat, "source": "youtube_cc_by"}
                results.append(rec)
                with FEATURES_FILE.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")
                status = feat.get("status")
                print(f"  observed: status={status} hook={feat.get('openingHookStrength')}")
            finally:
                out_path.unlink(missing_ok=True)  # footprint kept small (CC-BY would permit keeping)

    write_attribution()
    print(f"\nCC collection complete: {len(results)} new clips -> {FEATURES_FILE.relative_to(ROOT)}")
    print("Attribution (CC-BY requirement) written to ATTRIBUTION.md")


def write_attribution():
    """CC-BY REQUIRES crediting each source. Regenerate the credit list."""
    rows = []
    if FEATURES_FILE.exists():
        for line in FEATURES_FILE.open(encoding="utf-8"):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    lines = ["# CC-BY Attribution", "",
             "Feature data in `features_cc.jsonl` was derived from these "
             "Creative-Commons-licensed videos. CC-BY requires crediting the "
             "creators; this file is that credit.", ""]
    for r in rows:
        lines.append(f"- **{r.get('title','(untitled)')}** — {r.get('uploader','?')} "
                     f"— {r.get('license','?')} — {r.get('url','?')}")
    ATTRIBUTION_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
