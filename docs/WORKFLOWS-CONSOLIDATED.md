# Consolidated CI/CD Workflows

**Date:** 2026-06-02  
**Change:** Consolidated 10 workflows into 2 unified master workflows  
**Status:** Active

---

## Before (10 Scattered Workflows)

❌ **Fragmented:**
- `automated-tests.yml` — Python/Node tests
- `convergence-validation.yml` — Consistency checks
- `deploy-aws.yml` — AWS ECS deployment
- `linear-ticket-gate.yml` — Linear ticket validation
- `mcp-tunnel-canary.yml` — MCP server health
- `orchestration-challenge-ci.yml` — Agent orchestration
- `oss-repo-validation.yml` — OSS repo checks
- `release-provenance.yml` — Release tracking
- `report-generation.yml` — PDF reports
- `static-surface-ci.yml` — Static surface validation

**Problems:**
- Unclear which workflow to check first
- Overlapping validation logic
- Multiple "is it green?" signals
- Hard to add/modify checks globally
- Noise in Actions tab
- Race conditions between parallel workflows

---

## After (2 Master Workflows)

✅ **Consolidated & Clear:**

### 1. **CI Workflow** (`.github/workflows/ci.yml`)

**Triggers:** Push to master, PRs to master, manual dispatch

**Runs in parallel:**
- ✓ `validate-repo` — Check required files, manifests, surfaces, links
- ✓ `test-python` — Pytest suite (all Python tests)
- ✓ `test-node` — Playwright and Node tests
- ✓ `convergence-check` — Repo contract, workflow structure
- ✓ `integration-checks` — Cloud mirrors config, MCP contract

**Final gate:** `all-checks` — Summary job that confirms all critical checks passed

**Result:** Single ✓ or ✗ that tells you if the repo is valid and testable

---

### 2. **Deploy Workflow** (`.github/workflows/deploy.yml`)

**Triggers:** Push to master only (production deployment)

**Steps:**
1. Verify prerequisites (Dockerfile, package.json, health endpoint)
2. Build Docker image (`lantern-garage:latest`)
3. Validate health endpoint in container
4. Simulate ECS deployment (or execute with AWS credentials)

**Result:** Docker image ready + deployment configuration validated

**Production gate:** When AWS credentials are configured, this pushes to ECR and updates ECS service

---

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Clarity** | "Which workflow do I check?" | "Is CI green? Then Deploy." |
| **Speed** | Sequential, many run twice | Parallel validation, once |
| **Maintenance** | Update 10 files for one change | Update 1 file for 1 check |
| **Debugging** | Workflow failure unclear | Clear which step failed |
| **Onboarding** | New devs lost in workflow noise | "Look at CI and Deploy" |

---

## Migration Path

**Old workflows** (deprecated but kept for reference):
- `automated-tests.yml` → Merged into `ci.yml` → `test-python`, `test-node`
- `static-surface-ci.yml` → Merged into `ci.yml` → `validate-repo`
- `oss-repo-validation.yml` → Merged into `ci.yml` → `validate-repo`
- `convergence-validation.yml` → Merged into `ci.yml` → `convergence-check`
- `deploy-aws.yml` → Consolidated into `deploy.yml`
- `orchestration-challenge-ci.yml` → Archived (optional PR-only check, can restore if needed)
- `linear-ticket-gate.yml` → Archived (Linear integration, can restore if needed)
- `mcp-tunnel-canary.yml` → Archived (MCP health, can add back if needed)
- `release-provenance.yml` → Archived (Release tracking, can restore if needed)
- `report-generation.yml` → Archived (Manual reports, can restore if needed)

**To restore any workflow:**
1. Rename from `.github/workflows/ARCHIVED/` back to `.github/workflows/`
2. Update trigger conditions as needed
3. Commit and push

---

## How to Use

### For developers:
```bash
# Push to feature branch
git push origin feature/my-change

# Check CI on PR
# → Look at GitHub Actions tab
# → Single "CI" workflow tells you if it's safe

# When merging to master
git push origin master

# → CI runs automatically
# → Then Deploy runs (builds + validates Docker image)
```

### For operators:
```
1. Push to master → CI runs (5-10 min)
2. All checks green? → Deploy runs (2-3 min)
3. Deploy complete → Central Hub + Lantern Garage live on AWS
```

### To add a new validation check:
1. Edit `.github/workflows/ci.yml`
2. Add a new job under the appropriate section (Validation, Tests, Convergence, Integration)
3. Make it depend on `all-checks` if it's critical
4. Push

---

## Status Signals

**On master push:**

| Signal | Meaning | Action |
|--------|---------|--------|
| ✅ CI passed | All validations green | Deploy will run |
| ❌ CI failed | Some check failed | Check logs, fix issue, push again |
| 🔄 CI running | Checks in progress | Wait 5-10 minutes |
| ✅ Deploy passed | Docker image built & validated | Lantern Garage live on AWS (with credentials) |

---

## Future: Optional Workflows

If you need to restore specialized workflows:

- **`orchestration-challenge-ci.yml`** — For MCP/agent testing (restore in `.github/workflows/`)
- **`mcp-tunnel-canary.yml`** — For MCP server health monitoring
- **`release-provenance.yml`** — For tagged releases
- **`report-generation.yml`** — For automated PDF reports

These can be kept in an `archived/` folder and restored as needed without cluttering the main flow.

---

## Questions

1. Do you want to keep any of the archived workflows active?
2. Should Deploy require a manual approval gate, or auto-deploy on master?
3. Want to add per-feature-branch deployment, or master-only?
