#!/usr/bin/env python3
"""
Σ₀ V11 research loop — collection driver.

Runs real YouTube Data API v3 collection (general + gaming Shorts, separately
queried so coverage matches the requested gaming categories) until the daily
quota budget is exhausted, writing progress to data/youtube/collect_log.jsonl
so the hourly report writer can read real, non-fabricated numbers.

Output:
    data/youtube/top5000_shorts.jsonl        (general Shorts, append-only)
    data/youtube/top5000_gaming_shorts.jsonl (gaming Shorts, append-only)
    data/youtube/collect_log.jsonl           (one line per batch, for reporting)

This is metadata-only (title, channel, stats, duration, tags, thumbnail URL).
No video content is downloaded here.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_shorts_collector_v2 import YouTubeShortsCollectorV2, _load_env_local  # noqa: E402

import os  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "youtube"
TOP_GENERAL = OUT_DIR / "top5000_shorts.jsonl"
TOP_GAMING = OUT_DIR / "top5000_gaming_shorts.jsonl"
LOG_FILE = OUT_DIR / "collect_log.jsonl"

QUOTA_SAFETY_BUFFER = 200  # stop this far below the daily budget


def log_event(event: dict) -> None:
    event["timestamp"] = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


def append_records(records, general_file: Path, gaming_file: Path) -> tuple[int, int]:
    general = [r for r in records if not r.get("is_gaming")]
    gaming = [r for r in records if r.get("is_gaming")]
    if general:
        with open(general_file, "a") as f:
            for r in general:
                f.write(json.dumps(r) + "\n")
    if gaming:
        with open(gaming_file, "a") as f:
            for r in gaming:
                f.write(json.dumps(r) + "\n")
    return len(general), len(gaming)


def main():
    _load_env_local(ROOT / ".env.local")
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        log_event({"event": "fatal", "reason": "no YOUTUBE_API_KEY set"})
        print("No YOUTUBE_API_KEY set — aborting", file=sys.stderr)
        sys.exit(1)

    collector = YouTubeShortsCollectorV2(api_key, str(OUT_DIR))

    batch_size = 5  # search.list calls per batch (100 units each)
    total_general = 0
    total_gaming = 0
    batches = 0

    log_event({"event": "loop_start", "quota_budget": collector.QUOTA_DAILY_BUDGET})

    while True:
        state = collector._load_quota_state()
        remaining = collector.QUOTA_DAILY_BUDGET - state["units_used"]
        if remaining < QUOTA_SAFETY_BUFFER:
            log_event({
                "event": "loop_stop_quota_exhausted",
                "units_used": state["units_used"],
                "budget": collector.QUOTA_DAILY_BUDGET,
                "total_general": total_general,
                "total_gaming": total_gaming,
                "batches": batches,
            })
            print(f"Quota near limit ({state['units_used']}/{collector.QUOTA_DAILY_BUDGET}) — stopping")
            break

        try:
            records = collector.collect_shorts_real(search_calls=batch_size)
        except Exception as e:  # noqa: BLE001
            log_event({"event": "batch_error", "error": str(e)})
            print(f"Batch error: {e}", file=sys.stderr)
            time.sleep(5)
            continue

        n_general, n_gaming = append_records(records, TOP_GENERAL, TOP_GAMING)
        total_general += n_general
        total_gaming += n_gaming
        batches += 1

        state = collector._load_quota_state()
        log_event({
            "event": "batch_complete",
            "batch_num": batches,
            "new_general": n_general,
            "new_gaming": n_gaming,
            "total_general": total_general,
            "total_gaming": total_gaming,
            "units_used": state["units_used"],
            "budget": collector.QUOTA_DAILY_BUDGET,
        })
        print(
            f"Batch {batches}: +{n_general} general, +{n_gaming} gaming "
            f"(totals: {total_general}/{total_gaming}, quota {state['units_used']}/{collector.QUOTA_DAILY_BUDGET})"
        )

        time.sleep(2)  # be polite to the API

    log_event({
        "event": "loop_end",
        "total_general": total_general,
        "total_gaming": total_gaming,
        "batches": batches,
    })
    print(f"Done. {total_general} general + {total_gaming} gaming Shorts collected this run.")


if __name__ == "__main__":
    main()
