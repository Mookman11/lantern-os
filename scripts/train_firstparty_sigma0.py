#!/usr/bin/env python3
"""
First-party Σ₀ trainer — the LEGITIMATE training half of the flywheel.

Trains an XGBoost regressor on (real edit features -> real published outcome)
pairs that the operator OWNS: features captured when Lantern rendered each
Short, joined to real performance numbers the operator recorded for their own
published content (see src/creator-intelligence/training/learning-store.js
recordRenderedFeatures / recordOutcome). This is the only outcome-labeled
training data obtainable without scraping anyone.

HONESTY GATE: refuses to train below MIN_SAMPLES and writes
{"status": "insufficient_data", ...} instead of fabricating a model. Initially
there will be 0 labeled rows (no Shorts published + reported yet), so this will
correctly report insufficient_data — that is the true state, not a failure.

Output (only when trained):
    models/sigma0-v11.json          (the model, handoff-requested filename)
    models/sigma0-v11.report.json   (real metrics)
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOIN_HELPER = ROOT / "scripts" / "_firstparty_join_helper.js"
MODELS_DIR = ROOT / "models"
MODEL_FILE = MODELS_DIR / "sigma0-v11.json"
REPORT_FILE = MODELS_DIR / "sigma0-v11.report.json"

MIN_SAMPLES = 30  # below this, any "model" would be noise; honest floor for first-party data

# Numeric feature columns we capture at render time (real editing decisions).
FEATURE_COLUMNS = [
    "durationSec", "segmentCount", "collapseRisk", "viralScore", "hookScore", "motionMean",
]


def load_labeled():
    proc = subprocess.run(["node", str(JOIN_HELPER), "engagement_rate"],
                          capture_output=True, text=True, timeout=60)
    try:
        return json.loads(proc.stdout.strip())
    except json.JSONDecodeError:
        return {"labelKey": "engagement_rate", "rows": [], "_helperError": proc.stderr[-300:]}


def to_matrix(rows):
    X, y = [], []
    for r in rows:
        f = r.get("features", {}) or {}
        X.append([float(f.get(c, 0) or 0) for c in FEATURE_COLUMNS])
        y.append(float(r.get("label", 0) or 0))
    return X, y


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    data = load_labeled()
    rows = data.get("rows", [])

    if len(rows) < MIN_SAMPLES:
        report = {
            "status": "insufficient_data",
            "n_labeled": len(rows),
            "min_required": MIN_SAMPLES,
            "labelKey": data.get("labelKey"),
            "note": (
                "Not enough OWNED, outcome-labeled first-party rows to train. This is the "
                "expected initial state: it grows only as Lantern-made Shorts are published "
                "and their real performance is recorded via recordOutcome(). No model written; "
                "nothing fabricated."
            ),
        }
        REPORT_FILE.write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return

    # Real training path (runs once enough owned labels exist).
    import numpy as np
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score

    X, y = to_matrix(rows)
    X, y = np.array(X, dtype=float), np.array(y, dtype=float)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    model = xgb.XGBRegressor(n_estimators=120, max_depth=4, learning_rate=0.05,
                             subsample=0.8, colsample_bytree=0.8, random_state=42)
    model.fit(X_train, y_train)
    pred = model.predict(X_val)
    model.save_model(str(MODEL_FILE))

    report = {
        "status": "trained",
        "n_labeled": len(rows),
        "n_train": int(len(X_train)),
        "n_val": int(len(X_val)),
        "labelKey": data.get("labelKey"),
        "features": FEATURE_COLUMNS,
        "val_mae": round(float(mean_absolute_error(y_val, pred)), 6),
        "val_r2": round(float(r2_score(y_val, pred)), 4),
        "feature_importances": dict(zip(FEATURE_COLUMNS, [float(v) for v in model.feature_importances_])),
        "model_path": str(MODEL_FILE.relative_to(ROOT)),
        "honesty_note": (
            "Trained on OWNED first-party (edit-features -> real published-outcome) pairs only. "
            "No scraped or third-party data. val_r2 reflects how well editing decisions predict "
            "the operator's own engagement_rate at this sample size."
        ),
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
