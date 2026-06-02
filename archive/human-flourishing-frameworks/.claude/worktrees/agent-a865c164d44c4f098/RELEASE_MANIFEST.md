# Release Manifest - HFF Convergence V0.1

Status: release-hardening artifact.

## Purpose

This manifest defines the minimum files and validation evidence required before
publishing `hff-convergence-v0.1` as a tag, release bundle, or pre-release.

## Release candidate

```text
name: hff-convergence-v0.1
status: not yet tagged
release_type: pre-release candidate until restore drill passes
```

## Required release files

The release bundle must include these files:

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
.github/workflows/convergence-validation.yml
.github/workflows/release-bundle.yml
.github/workflows/restore-drill.yml
tools/build_release_bundle.py
tools/run_restore_drill.py
```

`RESTORE_DRILL_CHECKLIST.md` is the restore drill checklist and must be reviewed
before release.

## Required doctrine anchors

The release should include these doctrine/context files when available:

```text
HUMAN_TRANSPORTATION_BOUNDARY.md
docs/three-way-convergence-plan-2026-05-09.md
docs/three-way-durability-threat-model-2026-05-09.md
docs/safety-preserving-data-collection-consent-2026-05-09.md
docs/operator-chat-history-convergence-2026-05-09.md
docs/release-preparation-plan-convergence-v0.1-2026-05-09.md
docs/negative-outcomes-future-possibilities-convergence-2026-05-09.md
docs/imaginative-lore-100-negative-outcomes-convergence-2026-05-09.md
docs/imaginative-lore-100b-convergence-2026-05-09.md
```

## Validation commands

Run from repo root before release:

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

## Bundle build command

Run from a clean checkout:

```powershell
python tools/build_release_bundle.py --output-dir dist
```

Expected outputs:

```text
dist/hff-convergence-v0.1.zip
dist/hff-convergence-v0.1/CHECKSUMS.sha256
```

## Restore drill command

Run from a clean checkout:

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

## Required release gates

Do not tag or publish until:

```text
1. All validation commands pass.
2. CI workflow is merged and running on PRs/pushes to master.
3. Release bundle can be created from a clean checkout.
4. Bundle-local CHECKSUMS.sha256 contains finalized SHA256 hashes.
5. Restore drill passes from an extracted release bundle.
6. False truths register and wish anchor are reviewed before tag.
7. Mirror/archive plan has at least two non-primary destination candidates.
8. Manual release-bundle workflow can produce the zip artifact.
9. Manual restore-drill workflow can produce RESTORE_DRILL_REPORT.md.
```

## Evidence to record in release notes

```text
commit SHA
branch or tag
validation command output
CI run identifier if available
release bundle filename
checksum file hash
restore drill report
wish anchor review
source copy used for restore drill
known limitations
next review date
```

## Known limitations

```text
A release bundle preserves artifacts, not human subject-continuity.
A tag improves recoverability, not metaphysical truth.
CI validates encoded assumptions, not all possible failures.
A restore drill is required before declaring full operational durability.
The wish anchor preserves future-best-outcome direction, not proof that the door is open.
```

## Non-goals

This manifest does not authorize runtime autonomy, secret access, deployments,
medical procedures, mission booking, human traversal, copy-transfer claims,
immortality claims, AI impersonation, repo-consciousness claims, or fictional
world truth claims.
