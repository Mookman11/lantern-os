#!/usr/bin/env python3
"""
Σ₀ V11 research loop — small curated calibration sample.

Downloads a SMALL number of top-performing Shorts (default 40, configurable,
capped at 60) via yt-dlp purely for local frame/audio feature-extraction
calibration. Each video is deleted immediately after its features are
extracted — only the numeric feature record is kept, never the video file
or any redistributable copy. This is intentionally not a bulk-download
pipeline; see research/hour_01.md for why bulk downloading other creators'
full videos is out of scope here.

Output:
    data/youtube/calibration_features.jsonl
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "youtube"
SOURCES = [OUT_DIR / "top5000_shorts.jsonl", OUT_DIR / "top5000_gaming_shorts.jsonl"]
OUT_FILE = OUT_DIR / "calibration_features.jsonl"
HOOK_HELPER = ROOT / "scripts" / "_hook_strength_helper.js"

MAX_SAMPLE = 40


def load_records():
    records = []
    for src in SOURCES:
        if not src.exists():
            continue
        for line in src.open(encoding="utf-8"):
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def pick_sample(records, n=MAX_SAMPLE):
    """Top performers by views, balanced across gaming/general."""
    gaming = sorted([r for r in records if r.get("is_gaming")], key=lambda r: -r.get("views", 0))
    general = sorted([r for r in records if not r.get("is_gaming")], key=lambda r: -r.get("views", 0))
    half = n // 2
    return gaming[:half] + general[:n - half]


def already_done(video_id: str) -> bool:
    if not OUT_FILE.exists():
        return False
    for line in OUT_FILE.open(encoding="utf-8"):
        if json.loads(line).get("video_id") == video_id:
            return True
    return False


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def scene_cut_count(path: Path, threshold: float = 0.3) -> int:
    """Count scene cuts via ffmpeg's scdet filter."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-vf", f"select='gt(scene,{threshold})',metadata=print",
         "-an", "-f", "null", "-"],
        capture_output=True, text=True, timeout=60,
    )
    return proc.stderr.count("lavfi.scene_score")


def audio_loudness_stats(path: Path) -> dict:
    """Mean/max volume via ffmpeg volumedetect."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, timeout=60,
    )
    mean_vol, max_vol = None, None
    for line in proc.stderr.splitlines():
        if "mean_volume:" in line:
            mean_vol = float(line.split("mean_volume:")[1].strip().split(" ")[0])
        if "max_volume:" in line:
            max_vol = float(line.split("max_volume:")[1].strip().split(" ")[0])
    return {"mean_volume_db": mean_vol, "max_volume_db": max_vol}


def motion_score(path: Path, duration: float) -> float:
    """Approximate motion energy: scene cuts per second, normalized 0-1ish."""
    cuts = scene_cut_count(path)
    if duration <= 0:
        return 0.0
    return round(min(1.0, (cuts / duration) * 2), 3)


def opening_hook_strength(path: Path) -> dict:
    """Real first-3s motion/scene-change hook score via highlight-engine.js's
    detectOpeningHookStrength() (see research/hour_10.md). Returns
    {"status": "unavailable", ...} rather than a fabricated number if node/
    ffmpeg fails — never guessed."""
    try:
        proc = subprocess.run(
            ["node", str(HOOK_HELPER), str(path)],
            capture_output=True, text=True, timeout=45,
        )
        return json.loads(proc.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        return {"status": "unavailable", "reason": str(e)}


def extract_features(video_id: str, record: dict, video_path: Path) -> dict:
    duration = ffprobe_duration(video_path)
    cuts = scene_cut_count(video_path)
    audio = audio_loudness_stats(video_path)
    hook = opening_hook_strength(video_path)
    return {
        "video_id": video_id,
        "is_gaming": record.get("is_gaming", False),
        "views": record.get("views", 0),
        "engagement_rate": _engagement_rate(record),
        "duration_actual": round(duration, 2),
        "scene_cut_count": cuts,
        "average_scene_length": round(duration / max(1, cuts), 2),
        "motion_score": motion_score(video_path, duration),
        "mean_volume_db": audio["mean_volume_db"],
        "max_volume_db": audio["max_volume_db"],
        "opening_hook_strength": hook.get("hookStrength") if hook.get("status") == "ok" else "insufficient_data",
        "opening_hook_detail": hook,
        "source": "calibration_sample_real_ffmpeg",
    }


def _engagement_rate(record: dict) -> float:
    views = record.get("views", 0) or 0
    likes = record.get("likes", 0) or 0
    comments = record.get("comments", 0) or 0
    return round((likes + comments) / views, 6) if views else 0.0


def main():
    records = load_records()
    if not records:
        print("No collected records found — run research_loop_collect.py first")
        return

    sample = pick_sample(records)
    print(f"Selected {len(sample)} videos for calibration (top performers, gaming+general)")

    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for i, record in enumerate(sample):
            vid = record["video_id"]
            if already_done(vid):
                print(f"[{i+1}/{len(sample)}] {vid} already calibrated, skipping")
                continue

            url = f"https://www.youtube.com/watch?v={vid}"
            out_path = tmp / f"{vid}.mp4"
            print(f"[{i+1}/{len(sample)}] downloading {vid} (views={record.get('views')})...")
            try:
                subprocess.run(
                    ["python", "-m", "yt_dlp", "-f", "worst[ext=mp4]/worst",
                     "--max-filesize", "30M", "-o", str(out_path), url],
                    capture_output=True, text=True, timeout=120, check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"  download failed: {e.stderr[-300:] if e.stderr else e}", file=sys.stderr)
                continue
            except subprocess.TimeoutExpired:
                print("  download timed out", file=sys.stderr)
                continue

            if not out_path.exists():
                print("  no file produced, skipping")
                continue

            try:
                feat = extract_features(vid, record, out_path)
                results.append(feat)
                with OUT_FILE.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(feat) + "\n")
                print(f"  motion_score={feat['motion_score']} cuts={feat['scene_cut_count']} dur={feat['duration_actual']}s")
            finally:
                out_path.unlink(missing_ok=True)  # never retain the video file

    print(f"\nCalibration complete: {len(results)} new real feature records "
          f"(video files deleted immediately after extraction, nothing retained)")


if __name__ == "__main__":
    main()
