# Σ₀ V11 Research Loop — Hour 3

**Phase:** Baseline XGBoost training (real data, honesty-gated)

## What happened

Ran `scripts/research_loop_train.py` against the 1,451-record metadata
feature set from Hour 1. `MIN_SAMPLES = 200` gate passed (1,451 ≥ 200), so
training proceeded rather than being marked `insufficient_data`.

**Real result** (80/20 train/val split, n_val=291):

| Metric | Value |
|---|---|
| Validation MAE | 0.01245 |
| Validation R² | 0.199 |

**Feature importances:**

| Feature | Importance |
|---|---|
| `is_gaming` | 0.482 |
| `duration` | 0.185 |
| `hook_strength_title_proxy` | 0.126 |
| `title_length` | 0.114 |
| `tag_count` | 0.093 |

## Discoveries

1. **R² = 0.199 is weak, as expected and stated up front** — metadata alone
   (title length, tag count, duration, hook-word density, gaming/general
   flag) explains roughly 20% of engagement-rate variance. This is honest
   and useful as a floor: any real visual/audio signal added later should
   beat this baseline meaningfully, or it isn't adding value.
2. **`is_gaming` is by far the strongest single predictor** (0.48 importance)
   — stronger than any title-derived signal. In this dataset, *which
   category a Short is in* predicts engagement_rate better than how the
   title is written. This is a real, if early, finding: category-specific
   scoring (separate gaming vs. general engagement-rate baselines) is
   probably more valuable than a single unified hook-word score.
3. Hour 1's near-zero `hook_strength_title_proxy` correlation gets partial
   support here too — it ranks 3rd of 5 features, ahead of tag_count but
   behind duration and category.

## Model output

`data/models/xgboost-v10.json` (trained model) +
`data/models/training_report.json` (full metrics, same numbers as above).

## Next hour

Break down engagement_rate by gaming sub-category (`query_source` field —
Call of Duty, Fortnite, Minecraft, etc.) to see whether the `is_gaming`
signal is really "gaming vs. not" or hiding more specific sub-category
effects worth scoring separately.
