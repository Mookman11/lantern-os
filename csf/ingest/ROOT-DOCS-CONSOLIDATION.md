# CSF Ingestion — Root-Level Doc Consolidation

**Status:** ready_to_ingest  
**Action after ingest:** delete source files from docs/  
**Priority:** low — cleanup pass

## Files Moved to docs/ (from root)

These were moved from root → docs/ on 2026-06-05 by the cleanup pass.
After CSF ingestion confirms content is indexed, delete the source files.

| File | Topic | Delete after ingest |
|------|-------|---------------------|
| docs/BLOAT_CLEANUP_ISSUE.md | Repo sprawl tracking | ✅ yes |
| docs/BOT-SETUP-GUIDE.md | Discord bot setup | ✅ yes |
| docs/CLEANUP.md | Cleanup log | ✅ yes |
| docs/DEPLOYMENT-GUIDE.md | Deployment instructions | ✅ yes |
| docs/DISCORD-BOT-QUICKSTART.md | Bot quickstart | ✅ yes |
| docs/DOCKER.md | Docker config notes | ✅ yes |
| docs/DREAM-JOURNAL-API-ENDPOINTS.md | API endpoint reference | keep as ref |
| docs/DREAM-JOURNAL-QUICKSTART.md | Quickstart | keep as ref |
| docs/DREAM-JOURNAL-ROADMAP.md | V1.0.0 roadmap | keep as ref |
| docs/PR-DREAM-JOURNAL.md | PR notes | ✅ yes |
| docs/QUICK-START.md | General quickstart | ✅ yes |
| docs/SUPPORT.md | Support contacts | ✅ yes |

## Folders Archived (to archive/)

These were active directories moved to archive/ for potential deletion:

| Folder | Was | Action |
|--------|-----|--------|
| archive/aws-deployment/ | AWS CloudFormation + deploy scripts | ingest config → delete |
| archive/ops/ | Docker/K8s deployment files | ingest → delete |
| archive/repo-seeds/ | MK1 suit reactor seed | ingest → delete |
| archive/profiles/ | User profile JSONs | ingest → delete |
| archive/templates/ | CSV/JSON templates | ingest → delete |

## CSF Ingest Command (when ready)
```bash
python src/csf_compress.py --input docs/BLOAT_CLEANUP_ISSUE.md --output data/csf/
python src/cadd_dollhouse_csf.py --ingest-dir docs/ --filter "*.md"
```
