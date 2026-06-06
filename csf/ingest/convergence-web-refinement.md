# Convergence Web Refinement — v1.0.2+ Roadmap

**Status:** Design contract — pending web research validation  
**Slot:** `dream_journal/convergence_web_refinement` (priority 8)  
**Owner:** Agent pool (any)  
**Effort estimate:** 2–3 sessions  
**Files to change:** `src/convergence_io_engine.py`, `.github/workflows/ci.yml`, `data/pcsf/*.pcsf.json`, `manifests/validation/`

---

## Problem

The current 12-phase convergence loop (`src/convergence_io_engine.py`) is effective but manual:

1. **No automated evidence collection** — receipts are JSON files written locally, not surfaced to CI.
2. **No promotion gate integration** — `promotion_ready=True` is a local check; GitHub Actions does not read it.
3. **No drift detection** — Phase 4 "state_objective" always returns `"unknown"` because there is no objective manifest.
4. **No rollback coupling** — convergence pass and git revert are not linked.
5. **Monoworkstream is shell-script enforced** — not backed by a GitHub App or branch protection rule.

## Proposed Refinements

### 1. Automated Evidence Collection (Phase 11 → CI Artifact)

**Current:** `record_evidence` writes to `manifests/evidence/convergence-*.json`.  
**Target:** Upload convergence receipt as a CI artifact + post a PR comment with the promotion verdict.

```yaml
# .github/workflows/ci.yml addition
- name: Convergence Evidence
  run: python src/convergence_io_engine.py loop > convergence-report.json
- name: Upload Evidence
  uses: actions/upload-artifact@v4
  with:
    name: convergence-evidence
    path: convergence-report.json
- name: PR Promotion Gate
  if: github.event_name == 'pull_request'
  run: |
    verdict=$(jq -r '.promotion_ready' convergence-report.json)
    if [ "$verdict" != "true" ]; then
      echo "::error::Convergence loop failed — promotion blocked"
      exit 1
    fi
```

### 2. Objective Manifest (Phase 4 Fix)

**Current:** `"objective": "unknown"` always.  
**Target:** Read `manifests/objective-v1.0.2.json` if present; fall back to parsing the PR title/body for objective keywords.

```python
# src/convergence_io_engine.py
OBJECTIVE_PATH = REPO_ROOT / "manifests" / "objective-current.json"

def _read_objective():
    if OBJECTIVE_PATH.exists():
        return json.loads(OBJECTIVE_PATH.read_text()).get("objective", "unknown")
    # Fallback: parse CHANGELOG [Unreleased] or PR body
    return "unknown"
```

### 3. Drift Detection Between Runs (Phase 1 Enhancement)

Compare current convergence receipt with previous run:

```python
def _detect_drift(current, previous_path):
    if not previous_path.exists():
        return {"status": "first_run", "drift": []}
    prev = json.loads(previous_path.read_text())
    drift = []
    for check in current["checks"]:
        prev_check = next((c for c in prev.get("checks", []) if c["id"] == check["id"]), {})
        if prev_check.get("state") != check["state"]:
            drift.append({"id": check["id"], "from": prev_check.get("state"), "to": check["state"]})
    return {"status": "drift_detected" if drift else "stable", "drift": drift}
```

### 4. Git-Coupled Rollback Path

If convergence fails post-merge, auto-tag the last known good commit:

```bash
# scripts/convergence-rollback.sh
LAST_GOOD=$(git log --grep="promotion_ready=True" --oneline -1 | cut -d' ' -f1)
git tag -f "convergence-good-${LAST_GOOD}" "$LAST_GOOD"
```

### 5. Branch Protection Rule for Monoworkstream

Replace shell-hook enforcement with a GitHub branch protection rule:

```yaml
# .github/workflows/monoworkstream-gate.yml
name: Monoworkstream Gate
on:
  pull_request:
    types: [opened, reopened, synchronize]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check open PR count
        run: |
          open_count=$(gh pr list --state open --json number --jq 'length')
          if [ "$open_count" -gt 1 ]; then
            echo "::error::Monoworkstream violation: $open_count PRs open"
            exit 1
          fi
```

---

## Implementation Order

1. **Phase A** — CI artifact upload + PR comment (1 session)
2. **Phase B** — Objective manifest parser + drift detection (1 session)
3. **Phase C** — Branch protection rule + rollback tag script (1 session)

---

## Validation

- [ ] `python src/convergence_io_engine.py loop` produces artifact in CI
- [ ] PR with `promotion_ready=false` is blocked by CI gate
- [ ] `manifests/objective-current.json` changes Phase 4 output
- [ ] Drift between two runs is detectable and reported
- [ ] `git tag -l "convergence-good-*"` shows rollback targets

---

## References (pending web search)

- GitOps promotion gates (GitLab / GitHub Actions patterns)
- Evidence-based deployment (Honeycomb / Datadog SRE practices)
- Monorepo CI convergence (Nx / Bazel / Rush build graph patterns)
- DORA metrics — deployment frequency, lead time, change failure rate

**Next action:** Run web search on "GitOps promotion gates evidence based deployment" and update References section.
