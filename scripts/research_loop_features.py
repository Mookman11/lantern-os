#!/usr/bin/env python3
"""
Σ₀ V11 research loop — metadata-derived feature extraction.

Computes whatever Σ₀-style features are honestly derivable from YouTube Data
API metadata alone (title, stats, duration, tags) for every record collected
in data/youtube/top5000_shorts.jsonl and top5000_gaming_shorts.jsonl.

Fields that require actual video frames/audio (motion_score, camera_movement,
facecam_position, hud_position, speech_density, beat_changes, etc.) are NOT
computed here and are explicitly marked "insufficient_data" rather than
guessed — see scripts/research_loop_calibration.py for the small curated
sample where those are computed from real frame/audio analysis.

Output:
    data/youtube/features_v11.jsonl
"""

import json
import re
import statistics
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "youtube"
SOURCES = [OUT_DIR / "top5000_shorts.jsonl", OUT_DIR / "top5000_gaming_shorts.jsonl"]
OUT_FILE = OUT_DIR / "features_v11.jsonl"
SUMMARY_FILE = OUT_DIR / "features_v11_summary.json"

# Video-content-dependent fields the handoff asked for that metadata alone
# cannot honestly produce.
INSUFFICIENT_DATA_FIELDS = [
    "hook_time", "first_action", "peak_action", "peak_density",
    "average_scene_length", "motion_score", "camera_movement",
    "zoom_frequency", "crop_style", "facecam_position", "hud_position",
    "speech_density", "silence_ratio", "music_intensity", "beat_changes",
    "loudness_curve",
]

HOOK_WORD_PATTERNS = [
    r"\bwait\b", r"\bwatch\b", r"\bnever\b", r"\binsane\b", r"\bcrazy\b",
    r"\byou won.t believe\b", r"\bhow\b", r"\bwhy\b", r"\b#\d+\b",
    r"\btop\b", r"\bbest\b", r"\bworst\b", r"\bclutch\b", r"\bepic\b",
]


def title_hook_strength(title: str) -> float:
    """Proxy signal: density of attention-grabbing words/patterns in the title."""
    title_lower = (title or "").lower()
    hits = sum(1 for p in HOOK_WORD_PATTERNS if re.search(p, title_lower))
    return round(min(1.0, hits / 4), 3)


def load_records():
    records = []
    for src in SOURCES:
        if not src.exists():
            continue
        for line in src.open(encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def compute_features(record: dict) -> dict:
    views = max(1, record.get("views", 0))
    likes = record.get("likes", 0)
    comments = record.get("comments", 0)
    engagement_rate = round((likes + comments) / views, 6)

    features = {
        "video_id": record["video_id"],
        "is_gaming": record.get("is_gaming", False),
        "query_source": record.get("query_source", ""),
        "duration": record.get("duration", 0),
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagement_rate": engagement_rate,
        "hook_strength_title_proxy": title_hook_strength(record.get("title", "")),
        "tag_count": len(record.get("tags", []) or []),
        "title_length": len(record.get("title", "") or ""),
        "channel_id": record.get("channel_id", ""),
        "thumbnail_url": f"https://i.ytimg.com/vi/{record['video_id']}/hqdefault.jpg",
    }
    for field in INSUFFICIENT_DATA_FIELDS:
        features[field] = "insufficient_data"
    return features


def main():
    records = load_records()
    if not records:
        print("No collected records found yet — run research_loop_collect.py first")
        return

    feats = [compute_features(r) for r in records]
    with OUT_FILE.open("w", encoding="utf-8") as f:
        for feat in feats:
            f.write(json.dumps(feat) + "\n")

    engagement_rates = [f["engagement_rate"] for f in feats]
    hook_scores = [f["hook_strength_title_proxy"] for f in feats]
    gaming_count = sum(1 for f in feats if f["is_gaming"])

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(feats),
        "gaming_records": gaming_count,
        "general_records": len(feats) - gaming_count,
        "engagement_rate": {
            "mean": round(statistics.mean(engagement_rates), 6),
            "median": round(statistics.median(engagement_rates), 6),
            "stdev": round(statistics.pstdev(engagement_rates), 6) if len(engagement_rates) > 1 else 0,
        },
        "hook_strength_title_proxy": {
            "mean": round(statistics.mean(hook_scores), 3),
            "median": round(statistics.median(hook_scores), 3),
        },
        "note": (
            "Visual/audio/timing fields (motion, camera, facecam, HUD, speech, "
            "beat timing) are metadata-derived 'insufficient_data' here — they "
            "require frame/audio access, which is computed only for the small "
            "curated calibration sample (see research_loop_calibration.py)."
        ),
    }
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
