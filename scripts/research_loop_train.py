#!/usr/bin/env python3
"""
Σ₀ V11 research loop — XGBoost training on real metadata features.

Trains a regressor predicting engagement_rate from the metadata-derived
features in data/youtube/features_v11.jsonl (real data, Hour 1). Only the
metadata-only feature set is large enough (n=1,451) to train meaningfully;
the calibration sample (n=28, real frame/audio features) is far too small
to train on and is reported observationally instead (see research/hour_02.md).

Refuses to train below MIN_SAMPLES and writes an insufficient_data marker
instead of fabricating a model.

Output:
    data/models/xgboost-v10.json   (model)
    data/models/training_report.json (real metrics — train/val split, not fabricated)
"""

import json
from pathlib import Path

import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

ROOT = Path(__file__).resolve().parent.parent
FEATURES_FILE = ROOT / "data" / "youtube" / "features_v11.jsonl"
MODEL_DIR = ROOT / "data" / "models"
MODEL_FILE = MODEL_DIR / "xgboost-v10.json"
REPORT_FILE = MODEL_DIR / "training_report.json"

MIN_SAMPLES = 200

FEATURE_COLUMNS = [
    "duration", "tag_count", "title_length", "hook_strength_title_proxy", "is_gaming",
]
TARGET_COLUMN = "engagement_rate"


def load_dataset():
    if not FEATURES_FILE.exists():
        return None
    rows = [json.loads(l) for l in FEATURES_FILE.open(encoding="utf-8")]
    return rows


def to_matrix(rows):
    X = []
    y = []
    for r in rows:
        X.append([
            r["duration"],
            r["tag_count"],
            r["title_length"],
            r["hook_strength_title_proxy"],
            1.0 if r["is_gaming"] else 0.0,
        ])
        y.append(r["engagement_rate"])
    return np.array(X, dtype=float), np.array(y, dtype=float)


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_dataset()

    if not rows or len(rows) < MIN_SAMPLES:
        report = {
            "status": "insufficient_data",
            "n_samples": len(rows) if rows else 0,
            "min_required": MIN_SAMPLES,
            "note": "Not enough real samples to train meaningfully — no model written.",
        }
        REPORT_FILE.write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return

    X, y = to_matrix(rows)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(
        n_estimators=100, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, random_state=42,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_val)
    mae = float(mean_absolute_error(y_val, pred))
    r2 = float(r2_score(y_val, pred))

    model.save_model(str(MODEL_FILE))

    importances = dict(zip(FEATURE_COLUMNS, [float(v) for v in model.feature_importances_]))

    report = {
        "status": "trained",
        "n_samples": len(rows),
        "n_train": len(X_train),
        "n_val": len(X_val),
        "target": TARGET_COLUMN,
        "features": FEATURE_COLUMNS,
        "val_mae": round(mae, 6),
        "val_r2": round(r2, 4),
        "feature_importances": importances,
        "model_path": str(MODEL_FILE.relative_to(ROOT)),
        "honesty_note": (
            "Trained on metadata-only features (no real motion/audio/visual "
            "signal at this sample size — see research/hour_02.md for why). "
            "val_r2 reflects how well title/duration/tag metadata alone "
            "predicts engagement_rate, which is expected to be weak; this is "
            "a baseline, not a claim that metadata is sufficient for virality "
            "prediction."
        ),
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
