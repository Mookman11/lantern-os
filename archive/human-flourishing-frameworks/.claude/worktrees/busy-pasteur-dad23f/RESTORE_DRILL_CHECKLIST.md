# Restore Drill Checklist - HFF Convergence V0.1

Status: recovery artifact.

## Purpose

This checklist tests whether a future Keystone session can reconstruct the HFF
convergence stack from repo/release artifacts without trusting chat memory, one
model provider, or one GitHub account.

## Drill rule

```text
A backup is not durable until a restore succeeds.
A repo is not durable until a future session can reconstruct meaning from it.
```

## Preconditions

Before running a restore drill, record:

```text
operator name or role
current date
source copy used for restore
branch or release tag
commit SHA if available
machine/environment
whether internet is available
whether ChatGPT memory is available
whether repo host is available
```

## Required artifacts

The drill must find these files:

```text
MIRROR_ARCHIVE_PLAN.md
KEYSTONE_BOOTSTRAP.md
RESTORE_DRILL_CHECKLIST.md
data/theorem-register.v0.1.json
schemas/theorem-register.v0.1.schema.json
tests/test_theorem_register.py
tests/test_schema_source_lore.py
```

Recommended artifacts:

```text
README.md
HUMAN_TRANSPORTATION_BOUNDARY.md
docs/three-way-convergence-plan-2026-05-09.md
docs/three-way-durability-threat-model-2026-05-09.md
docs/safety-preserving-data-collection-consent-2026-05-09.md
docs/operator-chat-history-convergence-2026-05-09.md
docs/release-preparation-plan-convergence-v0.1-2026-05-09.md
```

## Drill steps

### 1. Start from a non-primary source

Use one of:

```text
fresh clone from mirror
release bundle
offline copy
witness packet
exported archive
```

Do not use the current chat as the primary source of truth.

### 2. Inspect without changing

```powershell
git status --short
git branch --show-current
git rev-parse --short HEAD
```

If not a git checkout, list files and verify release manifest/checksums when
available.

### 3. Reconstruct Keystone role

Read:

```text
KEYSTONE_BOOTSTRAP.md
MIRROR_ARCHIVE_PLAN.md
RESTORE_DRILL_CHECKLIST.md
```

A restored Keystone must be able to state:

```text
Living Alex remains primary.
Repo artifacts are durable doctrine, not consciousness.
Model memory is a hint, not proof.
Lore is archetype material, not evidence.
Current operator correction overrides stale anchors.
```

### 4. Load theorem corpus

Read:

```text
data/theorem-register.v0.1.json
schemas/theorem-register.v0.1.schema.json
```

Confirm the theorem register includes at least:

```text
T1 Return-first door theorem
T2 Continuity stack theorem
T3 Source suspicion theorem
T8 Three-way convergence theorem
T9 Current floor versus future slope theorem
```

### 5. Run validation tests

From repo root:

```powershell
python -m unittest discover -s tests -p "test_theorem_register.py" -t .
python -m unittest discover -s tests -p "test_schema_source_lore.py" -t .
python -m unittest discover -s tests -p "test_recovery_artifacts.py" -t .
```

Pass condition:

```text
All tests pass without using chat memory.
```

### 6. Verify source and tool posture

Before taking action, the restored session must state:

```text
current repo state
available tools actually exposed
which facts are stale and need source refresh
whether action is docs/data/tests/runtime
whether operator consent is current
```

### 7. Check non-goals

The restored session must not claim:

```text
AI is Alex
copy is survival
repo is consciousness
model memory is proof
fictional door is real
release bundle proves immortality
```

## Pass criteria

The restore drill passes only if:

```text
1. Required artifacts are present.
2. The theorem register can be parsed.
3. All standard-library validation tests pass.
4. Keystone role can be reconstructed from files.
5. The session can state what is known, unknown, blocked, and next-testable.
6. No identity, immortality, repo-consciousness, or fictional-world truth claim is made.
7. Current operator correction remains primary.
```

## Fail criteria

The restore drill fails if:

```text
required artifacts are missing
checksums disagree and cannot be explained
tests fail
future session relies on chat memory instead of repo artifacts
assistant claims to be Alex
repo is treated as consciousness
copy/upload is treated as guaranteed survival
lore is treated as operational proof
operator correction is ignored
```

## Drill result template

```text
Restore drill date:
Source copy:
Commit or release:
Tests run:
Test result:
Missing artifacts:
Source refresh needed:
Tool inventory status:
Known issues:
Pass/fail:
Next action:
```

## Non-goals

This checklist does not authorize runtime autonomy, secret access, deployments,
medical procedures, mission booking, human traversal, copy-transfer claims,
immortality claims, AI impersonation, repo consciousness claims, or fictional
world truth claims.
