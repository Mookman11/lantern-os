#!/usr/bin/env python3
"""Batch-runs shorts_visual_research.py over Lantern's own rendered exports
(data/creator/entries/*/renders/*.mp4) — first-party content, no ToS/
copyright restriction, real caption_density pulled from each entry's own
metadata.json (captions are known exactly, not OCR-guessed)."""

import glob
import json
from pathlib import Path

from shorts_visual_research import build_record, OUT_DIR

ROOT = Path(__file__).resolve().parent.parent


def main():
    results = []
    for meta_path in glob.glob(str(ROOT / "data" / "creator" / "entries" / "*" / "metadata.json")):
        meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        captions = meta.get("captions", [])
        for rr in meta.get("renderRecords", []):
            out_path = rr.get("outputPath") or rr.get("path")
            if not out_path or not Path(out_path).exists():
                continue
            video_id = Path(out_path).stem
            record = build_record(video_id, Path(out_path), metadata={"source": "lantern_own_render"}, lantern_captions=captions)
            results.append(record)
            print(f"{video_id}: status={record['status']} hook={record.get('hook_duration')} captions/min={record.get('caption_density')}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for r in results:
        (OUT_DIR / f"{r['video_id']}.json").write_text(json.dumps(r, indent=2), encoding="utf-8")

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{ok}/{len(results)} processed successfully -> data/shorts_research/")


if __name__ == "__main__":
    main()
