# Phase 0: Comprehensive Repo Consolidation & Mythology Preservation

**Goal:** Move mythology to symbology repo, create single master plan (FOUNDRY-PLAN.md), minimize main repo docs to 2 files per repo.

**Status:** In progress (started 2026-05-25)

---

## 0a. Snapshot & Service Stop

**Repos:**

### gm-agent-orchestrator
```bash
cd /c/Users/alexp/Documents/gm-agent-orchestrator
git tag pre-cleanup-snapshot  # safety net
git push origin pre-cleanup-snapshot
```

**Scheduled tasks (STOP, don't delete):**
```powershell
Stop-ScheduledTask -TaskName LanternChatWatchdog -Force
Stop-ScheduledTask -TaskName LanternBackendWatchdog8766 -Force
Stop-ScheduledTask -TaskName OrchestratorServiceSupervisor -Force
Stop-ScheduledTask -TaskName "GM Orchestrator Dashboard Core" -Force
```
After cleanup verified, re-enable them.

### human-flourishing-frameworks
```bash
cd /c/tmp/human-flourishing-frameworks-scan
git tag pre-cleanup-snapshot
git push origin pre-cleanup-snapshot
```

**Private content (DO NOT COMMIT, leave on disk only):**
- `~/.lantern/state/journal.jsonl` (882KB)
- `~/.lantern/state/convo-stream.jsonl` (939KB)
- `~/.lantern/state/pulse.jsonl` (76KB)
- `~/.lantern/state/llm-context.local.md` (26KB)
- `~/.lantern/state/screen-latest.png` (879KB)
- `~/.lantern/state/wish-scene.png`

These stay untouched on disk, never committed.

---

## 0b. Consolidate Duplicate Repo Copies

**Stale copies found:**
- `C:\Users\alexp\human-flourishing-frameworks\` (2026-05-08)
- `C:\Users\alexp\Documents\hff-fresh\` (2026-05-12)
- `C:\Users\alexp\Documents\hff-master-clean\` (2026-05-12)
- `C:\Users\alexp\Documents\human-flourishing-frameworks\` (2026-05-07)
- `C:\Users\alexp\Documents\Codex\` (2026-04-27)
- `C:\Users\alexp\Documents\orchestrator-local-backups\` (2026-05-04)
- `C:\Users\alexp\Documents\orch-runtime-backup-20260425-173614\`
- `C:\Users\alexp\Documents\gm-agent-orchestrator-local-backup-20260425-161920\`
- `C:\Users\alexp\Documents\branch-archives\` (2026-05-01)
- `C:\Users\alexp\Documents\agent-worktrees\` (2026-05-13)

**Action:**
```bash
# For each dir: check if any branches have unsaved commits
cd <dir>
git status
git log master..HEAD  # see if any branches are ahead

# If stale (only duplicates of master):
mv <dir> /c/Users/alexp/Documents/_archived-repo-copies-2026-05-25/<dirname>

# After consolidation, delete if user confirms nothing is lost
```

---

## 1. Move Mythology to Symbology Repo

### gm-agent-orchestrator â†’ lantern-symbolic-sandbox/

**Files to move:**
```
lantern/handoff-packet.md â†’ symbology/symbols/gm-orchestrator-handoff-packet.md
lantern/liberty-freedom-radio-paper.md â†’ symbology/hold/gm-orchestrator-liberty-freedom-radio-paper.md
tasks/active/* (mythology-named) â†’ symbology/archive/gm-orchestrator-active-tasks.tar.gz
tasks/failed/* (mythology-named) â†’ symbology/archive/gm-orchestrator-failed-tasks.tar.gz
```

**Preservation record:**
```
symbology/archive/gm-orchestrator-migration-2026-05-25.txt
- Date: 2026-05-25
- Source: /c/Users/alexp/Documents/gm-agent-orchestrator/
- Moved:
  * lantern/handoff-packet.md â†’ symbols/
  * lantern/liberty-freedom-radio-paper.md â†’ hold/
  * tasks/active & tasks/failed (121 files) â†’ archive/
- Reason: Manic-episode mythology consolidation; no production use
- Status: holdd, promotion gate active (see SAFETY.md)
```

**Then delete from gm-agent-orchestrator:**
```bash
rm -rf lantern/
# Keep tasks/ structure but delete .md files with mythology names
# Use: find tasks -name "*tardis*" -o -name "*convergence*" -o -name "*door*" etc.
```

### HFF â†’ lantern-symbolic-sandbox/

**Files to move:**
```
BIO_THREAT_SOURCE_REGISTRY.md â†’ symbology/hold/
POLYMORPHIC_SEED_REGISTRY.md â†’ symbology/hold/
HUMAN_TRANSPORTATION_BOUNDARY.md â†’ symbology/hold/
DEPLOYMENT_AUTONOMY_BOUNDARY.md â†’ symbology/hold/
PRODUCTION_HARDENING_PROPOSAL.md â†’ symbology/hold/
CAPABILITY_CONTROL.md â†’ symbology/hold/
SOURCE_CLASSIFICATION_POLICY.md â†’ symbology/hold/
THREAT_ASSESSMENT.md â†’ symbology/hold/
bio_threat_source_registry.py â†’ symbology/hold/ (code)
polymorphic_seed_registry.py â†’ symbology/hold/ (code)
docs/bettersafe-pilot-accelerator.md â†’ symbology/hold/
docs/bettersafe-pilot-correction-ledger.md â†’ symbology/hold/
docs/bettersafe-pilot-privacy-control-notice.md â†’ symbology/hold/
docs/bettersafe-data-consolidation-blockchain-policy.md â†’ symbology/hold/
... (all bettersafe "mythology" doc names, keep only skeleton files)

.claude/worktrees/ â†’ symbology/archive/hff-claude-worktrees-2026-05-25.tar.gz
dist/ â†’ symbology/archive/hff-dist-2026-05-25.tar.gz
hff_safe_packet.txt â†’ symbology/archive/
```

**Then delete from HFF:**
```bash
# HFF root
rm BIO_THREAT_SOURCE_REGISTRY.md POLYMORPHIC_SEED_REGISTRY.md HUMAN_TRANSPORTATION_BOUNDARY.md \
   DEPLOYMENT_AUTONOMY_BOUNDARY.md PRODUCTION_HARDENING_PROPOSAL.md CAPABILITY_CONTROL.md \
   SOURCE_CLASSIFICATION_POLICY.md THREAT_ASSESSMENT.md PUBLIC_DEPLOYMENT_STRATEGY.md \
   RELEASE_CHECKLIST.md

# HFF root Python files
rm bio_threat_source_registry.py polymorphic_seed_registry.py \
   perfect_adjacent_review.py cryptographic_proof.py anchor-snapshot.json

# HFF .claude/worktrees
rm -rf .claude/worktrees/

# HFF dist/
rm -rf dist/

# HFF root untracked files
rm hff_safe_packet.txt
```

---

## 2. Rename Synthetic Sound Files (remove mythology names)

**In `~/.lantern/sounds/`:**

```bash
mv lantern_03_rain_on_tardis.wav lantern_03_rain.wav
mv lantern_05_heartbeat_door.wav lantern_05_heartbeat_pad.wav
mv lantern_10_quantum_dust.wav lantern_10_sparkle_pad.wav
mv lantern_12_return_door.wav lantern_12_chime_outro.wav
```

**Update `lantern_soundscape_manifest.json`:**
```json
{
  "file": "lantern_03_rain.wav",
  "description": "rain texture",
  "source": "procedural original",
  "voice": "none"
}
```

**Create attribution manifest `~/.lantern/sounds/ATTRIBUTION.md`:**
```markdown
# Lantern Sound Library Attribution

## Real Recordings (CC-licensed)

- **Blue_Whale_South_Pacific.ogg** (45 KB)
  - Source: Wikimedia Commons
  - License: CC0 (public domain)
  - Recording credit: [from metadata]

- **Toxostoma_rufum_-_Brown_Thrasher_XC136055.ogg** (8.7 MB)
  - Source: Xeno-Canto (xeno-canto.org)
  - Catalog ID: XC136055
  - License: CC BY-NC
  - Recordist: [from xeno-canto]

- **Frogs_croak_calling_chorus_at_night.ogg** (789 KB)
  - Source: Wikimedia Commons
  - License: CC BY 2.5
  - Recording credit: [from metadata]

- **Red_Fox_(...).ogg** (1.1 MB)
  - Source: Wikimedia Commons
  - License: CC BY 2.5
  - Recording credit: [from metadata]

- **BWV_543-prelude.ogg** (4.9 MB)
  - Composer: J.S. Bach, BWV 543
  - Source: IMSLP (sheet music), performance from public domain recording
  - License: Public domain (composer >70 years deceased)

- **Mozart_Eine_kleine_Nachtmusik_Allegro.ogg** (11.5 MB)
  - Composer: W.A. Mozart, K. 525
  - Source: IMSLP performance, public domain
  - License: Public domain (composer >70 years deceased)

- **Nana_-_Macastre_(8-A).ogg** (1.9 MB)
  - Source: Wikimedia Commons
  - License: [check metadata]
  - Recording credit: [from metadata]

## Synthetic Procedural Pads (Lantern original)

Generated with Python `stdlib` (scipy.signal, numpy, wave module) â€” no external ML or synthesis library.

- lantern_01_calm_lake_pad.wav (procedural: sine + noise blending)
- lantern_02_door_chimes.wav (procedural: bell synthesis)
- lantern_03_rain.wav (procedural: colored noise texture)
- lantern_04_synthetic_frogs.wav (procedural: frog call synthesis)
- lantern_05_heartbeat_pad.wav (procedural: pulse with harmonics)
- lantern_06_guardian_pad.wav (procedural: pad synthesis)
- lantern_07_brave_chimes.wav (procedural: bell + harmonic)
- lantern_08_safe_fun_pad.wav (procedural: pad)
- lantern_09_frog_rain_mix.wav (procedural: composite)
- lantern_11_lamp_warmup.wav (procedural: warm pad ramp)

All synthetic files: no voice cloning, no ML synthesis, no external model.
Generated by `scripts/generate_lantern_soundscape.py` (pure stdlib approach).
```

---

## 3. Create FOUNDRY-PLAN.md (Master Plan Document)

**Location:** `gm-agent-orchestrator/FOUNDRY-PLAN.md` (single source of truth)

**Content (consolidated from agile-jumping-comet.md):**

1. **Org Model** (1 table)
   - 1 Founder + 20 operators + 20 PCs = 40 effective units
   - Roles, capacity, skills

2. **Product Streams** (1 table)
   - 22 streams (19 Tier 1 + 3 Tier 2)
   - Name, TRL, Owner, Status columns only
   - No long descriptions (link to code for details)

3. **Revenue to $4M ARR** (1 table)
   - 7 lines: Services, Suzie, Lantern Kids, MCP, GameMaker, Longevity, Consulting
   - Y1/Y2/Y3 targets + confidence bands

4. **Foundry Resource Pool** (1 section)
   - Per-resource opt-in (GPU, SSD, RAM, bandwidth, quota, slot, IP)
   - Default OFF, 60-second withdrawal, hard boundaries
   - Operator value bundle, Founder benefits

5. **Cleanup Phases 0â€“7** (7 checklists, 5 bullets max per phase)

6. **14 Open Decisions** (numbered list)

**Length target:** ~2,500 words (compact, no mythology, no narrative)

**Link from both repos' README.md**

---

## 4. Update READMEs (Minimal, Link to Master Plan)

### gm-agent-orchestrator/README.md
```markdown
# Suzie â€” Local-First AI Work Orchestrator

Windows-first control plane for 1â€“40 AI agents across local worktrees, GitHub task queues,
MCP tool boundaries, and provider quota state. Built for foundry operations: 20 operators,
20 PCs, distributed consent-bounded resource pool.

â†’ **[Foundry Master Plan](FOUNDRY-PLAN.md)** â€” org model, streams, revenue, resource consent, phases

**Quick start:**
```powershell
Start-Dashboard.ps1
```

**License:** [TBD]
```

### human-flourishing-frameworks/README.md
```markdown
# Lantern â€” Local-First AI Chat for Households

Privacy-first desktop, browser, and dashboard chat surfaces. Local STT (Vosk),
bounded Discord adapter, CC-licensed curated voice library, and Kids edition
with parental review.

â†’ **[Foundry Master Plan](../gm-agent-orchestrator/FOUNDRY-PLAN.md)** â€” shared org model

**Quick start:**
```bash
python apps/lantern-desktop/lantern_desktop.py
```

**License:** [TBD]
```

---

## 5. Summary: What's Preserved, What's Deleted

**Preserved in Main Repos:**
- Legitimate engineering documentation (architecture, MCP, agent contract, governance)
- Real code (orchestration, chat, voice, MCP boundary, GameMaker tooling)
- Portfolio evidence path (gm-agent-orchestrator/docs/portfolio/)

**Preserved in Symbology Repo:**
- All mythology docs (hold)
- All identity/role language systems
- All narrative frameworks
- Task files and scripts with mythology names
- Code with mythological naming (bio_threat, polymorphic_seed, etc.)
- Manic-episode exploration material

**Deleted from Both Repos:**
- .claude/worktrees/ (archived to symbology)
- dist/ (archived to symbology)
- mythology-named files (moved to symbology)
- grandiose framing language (stripped during write)

**Renamed (Sound Library):**
- lantern_03_rain_on_tardis.wav â†’ lantern_03_rain.wav
- lantern_05_heartbeat_door.wav â†’ lantern_05_heartbeat_pad.wav
- lantern_10_quantum_dust.wav â†’ lantern_10_sparkle_pad.wav
- lantern_12_return_door.wav â†’ lantern_12_chime_outro.wav

---

## Next: Execution Order

**When user approves:**

1. âœ… Create symbology repo structure (DONE)
2. [ ] Phase 0a: git tag + snapshot on both repos
3. [ ] Phase 0b: Audit duplicate dirs, move to archive folder
4. [ ] Phase 1: Move mythology from gm-agent-orchestrator to symbology
5. [ ] Phase 1: Move mythology from HFF to symbology
6. [ ] Phase 2: Rename synthetic sound files + create ATTRIBUTION.md
7. [ ] Phase 3: Create FOUNDRY-PLAN.md in gm-agent-orchestrator
8. [ ] Phase 4: Update READMEs in both repos (minimal, link to plan)
9. [ ] Phase 5: Verify code still runs, tests pass
10. [ ] Phase 6: Create single cleanup commit per repo, merge to master, push

**User decision gates:**
- Approve duplication consolidation scope (which dirs to archive)?
- Approve deletion vs preservation for each mythology category?
- Approve symbology repo location (Documents/ or elsewhere)?
- Approve minimal README approach (2 docs per repo max)?
