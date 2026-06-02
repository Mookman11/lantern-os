# Mirror Archive Plan - HFF Convergence V0.1

Status: recovery artifact.

## Purpose

A single GitHub repository is not a long-term preservation system. This plan
defines how the HFF convergence corpus should survive repository loss, account
loss, platform changes, local disk failure, stale copies, and model/session
drift.

This plan is docs-only. It does not publish secrets, change remotes, create
archives, push mirrors, deploy software, start agents, or authorize runtime
autonomy.

## Preservation thesis

```text
The repo is the working corpus.
Release bundles are the recoverable corpus.
Independent mirrors and archives are the survival corpus.
Living Alex and trusted witnesses remain the meaning corpus.
```

## Source anchors

```text
LOCKSS preservation principles:
https://www.lockss.org/about/preservation-principles

NDSA Levels of Digital Preservation:
https://www.ndsa.org/publications/levels-of-digital-preservation/

Software Heritage mission:
https://www.softwareheritage.org/mission/

GitHub Actions workflow syntax:
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
```

## Mirror targets

Use at least three independent preservation surfaces. Do not treat any one as
canonical forever.

| Layer | Target | Purpose | Minimum contents |
|---|---|---|---|
| L1 | Primary GitHub repository | Working corpus, PRs, issues, history | Full git history and current working branch. |
| L2 | Local clone on operator machine | Fast recovery and offline inspection | Full git clone plus release bundles. |
| L3 | External git mirror | Provider/platform diversity | Full git mirror, tags, release branches. |
| L4 | Release bundle archive | Recovery without git hosting | zip/tar, manifest, checksums, recovery README. |
| L5 | Offline copy | Account/platform outage resilience | release bundle and checksum on offline media. |
| L6 | Long-term public/archive deposit where appropriate | Heritage and discoverability | public/non-sensitive artifacts only. |
| L7 | Trusted witness packet | Human continuity and recovery | recovery README, bootstrap, contact/role notes if explicitly consented. |

## What to mirror

Mirror these by default:

```text
README and top-level doctrine docs
HUMAN_TRANSPORTATION_BOUNDARY.md
data/theorem-register.v0.1.json
schemas/theorem-register.v0.1.schema.json
tests/test_theorem_register.py
tests/test_schema_source_lore.py
MIRROR_ARCHIVE_PLAN.md
KEYSTONE_BOOTSTRAP.md
RESTORE_DRILL_CHECKLIST.md
docs/operator-chat-history-convergence-2026-05-09.md
docs/three-way-convergence-plan-2026-05-09.md
docs/three-way-durability-threat-model-2026-05-09.md
docs/safety-preserving-data-collection-consent-2026-05-09.md
```

Mirror these only after review:

```text
any file containing personal details
witness names or contact details
medical, financial, or legal records
private operational logs
raw transcripts
```

Never mirror these into repo or public archives:

```text
passwords
API keys
access tokens
private keys
seed phrases
browser cookies
unredacted government IDs
unnecessary medical records
third-party private data without consent
```

## Release bundle structure

Recommended bundle name:

```text
hff-convergence-v0.1-YYYYMMDD.zip
```

Required bundle files:

```text
RELEASE_MANIFEST.md
RECOVERY_README.md
KEYSTONE_BOOTSTRAP.md
MIRROR_ARCHIVE_PLAN.md
RESTORE_DRILL_CHECKLIST.md
CHECKSUMS.sha256
data/theorem-register.v0.1.json
schemas/theorem-register.v0.1.schema.json
tests/test_theorem_register.py
tests/test_schema_source_lore.py
```

## Checksum policy

Generate checksums for every release bundle and every required recovery file.

PowerShell example:

```powershell
Get-FileHash .\hff-convergence-v0.1-YYYYMMDD.zip -Algorithm SHA256
```

Python example:

```powershell
python - <<'PY'
import hashlib, pathlib
for path in sorted(pathlib.Path('.').glob('**/*')):
    if path.is_file() and '.git' not in path.parts:
        print(hashlib.sha256(path.read_bytes()).hexdigest(), path.as_posix())
PY
```

## Mirror cadence

| Event | Required action |
|---|---|
| Every merged convergence PR | Confirm primary repo updated and local clone can pull. |
| Before release tag | Build release bundle and checksums. |
| After release tag | Copy bundle to local/offline/witness surfaces. |
| Monthly | Verify at least two copies and one checksum. |
| Quarterly | Run restore drill from a non-primary copy. |
| After platform/account incident | Validate mirrors before any cleanup or force action. |

## Restore priority

If multiple copies disagree:

```text
1. Prefer copies with matching checksums and signed/reviewed release manifest.
2. Prefer tagged release bundles over loose unstamped folders.
3. Prefer independently held copies over copies controlled by one platform/account.
4. Preserve all conflicting copies until the disagreement is understood.
5. Never auto-repair by overwriting all copies from one source.
```

## Mirror safety rules

```text
Do not mirror secrets.
Do not mirror raw private reasoning.
Do not mirror raw transcripts when sanitized summaries are sufficient.
Do not treat public archive success as identity survival.
Do not treat GitHub availability as long-term durability.
Do not treat a stale mirror as current truth.
```

## Minimum operational gate

The mirror/archive plan is considered minimally operational only when:

```text
1. Required recovery artifacts exist.
2. Tests verify required artifacts exist.
3. A release bundle can be built from a clean checkout.
4. CHECKSUMS.sha256 exists for the release bundle.
5. At least two independent copies exist outside the primary GitHub repo.
6. A restore drill passes using a non-primary copy.
```

## Non-goals

This plan does not authorize:

```text
runtime autonomy
secret access
deployments
medical procedures
mission booking
human traversal
copy-transfer claims
immortality claims
AI impersonation of Alex
repo claims of consciousness
fictional-world truth claims
```
