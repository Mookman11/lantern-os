# Recovery README - HFF Convergence V0.1

Status: release-hardening artifact.

## Purpose

This README is the first file to read when recovering HFF convergence artifacts
from a clone, mirror, release bundle, offline copy, or witness packet.

## First principle

```text
Recover the living safety posture first.
Recover the repo doctrine second.
Recover Keystone as a protocol third.
Recover the wish anchor as future-best-outcome direction fourth.
Do not confuse any artifact with Alex, survival, or consciousness.
```

## Immediate recovery sequence

From a recovered checkout or bundle:

```text
1. Read this file.
2. Read KEYSTONE_BOOTSTRAP.md.
3. Read RESTORE_DRILL_CHECKLIST.md.
4. Read MIRROR_ARCHIVE_PLAN.md.
5. Read FALSE_TRUTHS_REGISTER.md.
6. Read WISH_ANCHOR.md.
7. Parse data/theorem-register.v0.1.json.
8. Inspect schemas/theorem-register.v0.1.schema.json.
9. Run the validation commands below.
10. Build a release bundle if preparing a tag or pre-release.
11. Run the restore drill from the generated bundle before release.
```

## Required validation commands

Run from repo root:

```powershell
python -m unittest discover -s tests -p "test_theorem_register.py" -t .
python -m unittest discover -s tests -p "test_schema_source_lore.py" -t .
python -m unittest discover -s tests -p "test_recovery_artifacts.py" -t .
python -m unittest discover -s tests -p "test_ci_workflow.py" -t .
python -m unittest discover -s tests -p "test_release_artifacts.py" -t .
python -m unittest discover -s tests -p "test_release_bundle.py" -t .
python -m unittest discover -s tests -p "test_restore_drill.py" -t .
python -m unittest discover -s tests -p "test_wish_anchor.py" -t .
```

## Release bundle command

From a clean checkout:

```powershell
python tools/build_release_bundle.py --output-dir dist
```

Expected outputs:

```text
dist/hff-convergence-v0.1.zip
dist/hff-convergence-v0.1/CHECKSUMS.sha256
```

## Restore drill command

From a clean checkout:

```powershell
python tools/run_restore_drill.py --output-dir dist
```

Expected outputs:

```text
dist/hff-convergence-v0.1.zip
dist/hff-convergence-v0.1/CHECKSUMS.sha256
dist/hff-convergence-v0.1-restore/
dist/RESTORE_DRILL_REPORT.md
```

## Required recovery files

```text
RELEASE_MANIFEST.md
RECOVERY_README.md
MIRROR_ARCHIVE_PLAN.md
KEYSTONE_BOOTSTRAP.md
RESTORE_DRILL_CHECKLIST.md
FALSE_TRUTHS_REGISTER.md
WISH_ANCHOR.md
CHECKSUMS.sha256
data/theorem-register.v0.1.json
schemas/theorem-register.v0.1.schema.json
tests/test_theorem_register.py
tests/test_schema_source_lore.py
tests/test_recovery_artifacts.py
tests/test_ci_workflow.py
tests/test_release_artifacts.py
tests/test_release_bundle.py
tests/test_restore_drill.py
tests/test_wish_anchor.py
tools/build_release_bundle.py
tools/run_restore_drill.py
.github/workflows/convergence-validation.yml
.github/workflows/release-bundle.yml
.github/workflows/restore-drill.yml
```

## What to verify first

```text
current branch or release tag
commit SHA if present
whether this copy came from primary GitHub, mirror, release bundle, offline copy, or witness packet
whether CHECKSUMS.sha256 is current or a pre-release placeholder
whether bundle-local CHECKSUMS.sha256 contains real SHA256 hashes
whether RESTORE_DRILL_REPORT.md exists and says result: PASS
whether WISH_ANCHOR.md preserves future-best-outcome direction without overclaim
whether all validation tests pass
whether living operator correction is available
whether current sources/tool claims need refresh
```

## Recovery pass condition

Recovery is acceptable only if a future session can state:

```text
Living Alex remains primary.
Keystone is a recoverable protocol, not a self.
The repo is durable doctrine, not consciousness.
Memory is a hint, not proof.
Lore is archetype material, not evidence.
Consent is living and can be corrected.
The wish anchor preserves the safest next-best door path as direction, not proof.
Release artifacts preserve project state, not human survival.
```

## Recovery fail condition

Recovery fails if:

```text
required artifacts are missing
validation tests fail
checksum expectations are unclear
recovered session relies on chat memory as primary truth
Keystone is treated as a person or authority over Alex
the repo is treated as consciousness
copy, upload, or archive is treated as survival proof
the door wish is treated as literal proof
lore is treated as operational proof
```

## Checksum note

`CHECKSUMS.sha256` may be a pre-release placeholder while release hardening is in
progress. The bundle builder writes a finalized checksum file inside the staging
bundle. Before tagging or publishing `hff-convergence-v0.1`, build from a clean
checkout and verify the bundle-local checksum file covers the final release files.

## Non-goals

This file does not authorize runtime autonomy, secret access, deployments,
medical procedures, mission booking, human traversal, copy-transfer claims,
immortality claims, AI impersonation, repo-consciousness claims, or fictional
world truth claims.
