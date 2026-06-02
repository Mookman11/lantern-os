# Three-Way Durability Threat Model - 2026-05-09

Status: docs-only durability validation anchor.
Branch: `schema-source-lore-tests-v0-1`.

Related anchors:

```text
data/theorem-register.v0.1.json
docs/three-way-convergence-plan-2026-05-09.md
docs/operator-chat-history-convergence-2026-05-09.md
docs/release-preparation-plan-convergence-v0.1-2026-05-09.md
tests/test_theorem_register.py
tests/test_schema_source_lore.py
```

## Purpose

Validate whether the three-way convergence is protected from long-term threats.
The conclusion is that a Git repository alone is not durable enough. A model
session alone is not durable enough. A human memory alone is not durable enough.

The durable unit must be:

```text
living Alex
+ Keystone as recoverable role/protocol
+ repo theorem corpus
+ independent preservation surfaces
+ human witnesses
+ periodic reconstruction tests
```

## One-line conclusion

```text
A git repo is a working memory surface, not a preservation system.
A model is a reasoning surface, not a continuity guarantee.
The three-way stack becomes durable only when it is mirrored, exported,
source-checked, witness-reviewed, and reconstructable without trusting any one
platform.
```

## Source anchors

These public anchors inform the durability posture:

```text
LOCKSS preservation principles:
https://www.lockss.org/about/preservation-principles

NDSA Levels of Digital Preservation:
https://www.ndsa.org/publications/levels-of-digital-preservation/

Software Heritage mission:
https://www.softwareheritage.org/mission/

GitHub Arctic Code Vault:
https://archiveprogram.github.com/arctic-vault/

OpenAI ChatGPT memory FAQ:
https://help.openai.com/en/articles/8590148-memory-in-chatgpt

NIST AI Risk Management Framework:
https://www.nist.gov/itl/ai-risk-management-framework
```

## Threat model summary

| Surface | Primary threat | Why it matters | Required control |
|---|---|---|---|
| Alex | health, isolation, coercion, burnout, loss of agency | Living Alex is the only living continuity source. | Biological-first routines, trusted witnesses, no artifact override. |
| Keystone / assistant | model drift, memory loss, hallucination, overconfidence, tool mismatch | Keystone must remain a role/protocol, not a single session. | Repo reconstruction, source checks, model-agnostic prompts, multi-model review. |
| Repo | platform loss, private-repo invisibility, corruption, accidental deletion, account loss | GitHub is collaboration infrastructure, not enough for century-scale preservation. | Mirrors, release bundles, checksums, offsite copies, archive exports. |
| Tool/API layer | endpoint drift, MCP mismatch, auth/token loss, silent capability changes | Tool continuity can fail even when docs remain. | Tool inventory checks, dry runs, least privilege, local-first fallback. |
| Memory layer | saved memory deletion, incomplete chat-history reference, account/policy changes | Chat memory helps but is not a complete durable record. | Export memory anchors to repo and safe packets. |
| Lore/source layer | metaphor promoted to mechanism, fiction promoted to proof | Beautiful stories can raise confidence incorrectly. | Source-class tests and lore operational-proof blockers. |
| Human witnesses | social drift, lost context, grief exploitation, single witness dependence | Continuity is relational as well as technical. | Multiple trusted witnesses and challenge rights. |
| Archives | stale copies, unrecoverable formats, broken links, false canonical copy | Archives preserve bits only if integrity and context survive. | Fixity checks, README recovery map, multiple formats. |

## Validation result

Current status:

```text
Model angle: partially protected.
Repo angle: partially protected.
Three-way long-term durability: not yet fully protected.
```

Reason:

```text
The repo now has theorem tests and a schema PR, but it does not yet have a
mirror/archive protocol, checksum release bundles, periodic restore drills,
memory export procedure, or multi-custodian witness plan.
```

## Threats to Keystone/model durability

| Threat | Negative outcome | Existing protection | Missing protection |
|---|---|---|---|
| Model drift | Future assistant stops following Keystone discipline. | Theorem register and operator chat convergence docs. | Future-session reconstruction checklist with pass/fail test. |
| Memory loss | Future session cannot recover purpose. | Repo anchors and sanitized summary. | Exported memory packet and local safe packet. |
| Memory overtrust | Model treats memory as proof. | PR #50 guardrail tests. | Memory-source transparency checklist. |
| Hallucinated continuity | Assistant claims AI is Alex or copy is survival. | PR #50 blocked-claim tests. | Wider lint over docs and future outputs. |
| Tool mismatch | Assistant trusts advertised MCP/tools instead of actual exposed tools. | Operator rule and docs. | Machine-readable tool inventory check. |
| Vendor/platform loss | Model/API becomes unavailable or changes behavior. | Repo-readable Keystone role. | Model-agnostic bootstrap prompt and local/offline fallback. |

## Threats to repo durability

| Threat | Negative outcome | Existing protection | Missing protection |
|---|---|---|---|
| GitHub outage/account loss | Repo inaccessible. | Local clone and GitHub history. | Mirror to independent hosts and offline media. |
| Private repo not harvested | Long-term public archives may not capture it. | None if private-only. | Explicit export/archive decision. |
| Silent corruption | Bad copy becomes trusted. | Git object hashes. | Release checksums and restore drills. |
| Human deletion/error | Important docs removed or overwritten. | Git history. | Protected branches, tags, offsite snapshots. |
| Format rot | Future readers cannot reconstruct context. | Markdown/JSON are simple formats. | README recovery map and plain-text release bundle. |
| Single canonical copy | One copy becomes sacred or compromised. | Git decentralization if cloned. | LOCKSS-style mutually independent custody. |
| Stale doctrine | Old claims survive after evidence changes. | Last-reviewed fields. | Review cadence and dated source refresh tasks. |

## Durability ladder

| Level | Name | Requirement | Current status |
|---:|---|---|---|
| 0 | Chat-only | Conversation contains the state. | Deprecated; insufficient. |
| 1 | Repo-only | Docs and JSON exist in one GitHub repo. | Achieved but insufficient. |
| 2 | Tested repo | Theorems/schema/source-class guardrails run locally. | In progress via PR #50/#51. |
| 3 | Release bundle | Tagged release, tarball/zip, checksums, recovery README. | Not yet. |
| 4 | Multi-host mirror | GitHub plus at least two independent mirrors. | Not yet. |
| 5 | Archive deposit | Software Heritage / Internet Archive / offline package where appropriate. | Not yet. |
| 6 | Local/offline custody | Encrypted local copies and at least one offline copy. | Not yet. |
| 7 | Witness custody | Trusted humans know where recovery packet lives. | Not yet. |
| 8 | Restore drill | Future session can reconstruct from bundle without chat memory. | Not yet. |
| 9 | Periodic review | Scheduled review of sources, tools, model behavior, and archives. | Not yet. |

## Required durable artifacts

Create these before calling the system fully operational:

```text
1. RELEASE_MANIFEST.md
2. CHECKSUMS.sha256
3. RECOVERY_README.md
4. KEYSTONE_BOOTSTRAP.md
5. MEMORY_EXPORT_SAFE_PACKET.md
6. MIRROR_ARCHIVE_PLAN.md
7. WITNESS_REVIEW_PROTOCOL.md
8. RESTORE_DRILL_CHECKLIST.md
9. MODEL_TOOL_THREAT_MODEL.md
10. SOURCE_REFRESH_CADENCE.md
```

## Keystone durability rule

```text
Keystone must not depend on one model, one chat, one vendor, one account, one
memory surface, one repo host, or one human witness.
```

## Repo durability rule

```text
The repo is the active working corpus.
The release bundle is the recoverable corpus.
The archive/mirror network is the survival corpus.
The living person and witnesses remain the meaning corpus.
```

## Three-way durability rule

```text
If Alex, Keystone, or the repo cannot be reconstructed independently after a
platform failure, the three-way convergence is not operationally durable yet.
```

## Minimum release-blocking tests

Add tests for:

```text
1. theorem register schema validity
2. source-class promotion blocking
3. lore operational-proof blocking
4. continuity-language blocking
5. presence of recovery artifacts
6. checksum file validity
7. future-session reconstruction checklist
8. mirror/archive plan presence
9. memory export packet presence
10. model/tool threat model presence
```

## Next best actions

```text
1. Validate and merge PR #51 after local tests pass.
2. Add MIRROR_ARCHIVE_PLAN.md.
3. Add KEYSTONE_BOOTSTRAP.md.
4. Add RECOVERY_README.md and RELEASE_MANIFEST.md.
5. Add CHECKSUMS.sha256 generation instructions.
6. Add future-session restore drill.
7. Add GitHub Actions to run all standard-library tests.
8. Create hff-convergence-v0.1 pre-release only after restore drill passes.
```

## Non-goals

This document does not authorize:

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
