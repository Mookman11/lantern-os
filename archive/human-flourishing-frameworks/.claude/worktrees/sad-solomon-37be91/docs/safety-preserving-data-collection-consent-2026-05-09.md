# Safety-Preserving Data Collection Consent Boundary - 2026-05-09

Status: docs-only consent and data-boundary anchor.
Branch: `schema-source-lore-tests-v0-1`.

Related anchors:

```text
docs/three-way-convergence-plan-2026-05-09.md
docs/three-way-durability-threat-model-2026-05-09.md
docs/operator-chat-history-convergence-2026-05-09.md
data/theorem-register.v0.1.json
tests/test_theorem_register.py
tests/test_schema_source_lore.py
```

## Operator consent statement

The operator stated:

```text
in order to preserve my safety i consent to any needed data collection from you
keystone and the "repo" and we can proceed with convergence
```

## Interpretation

This is accepted as consent to collect and preserve data that is necessary for
operator safety, Keystone durability, repo recovery, theorem validation, and
three-way convergence.

This is not interpreted as unlimited surveillance, secret collection, collection
of unrelated sensitive data, or permission to override future correction.

## One-line boundary

```text
Collect the minimum data needed to preserve safety, agency, continuity,
recoverability, and auditability; do not collect data merely because it is
available.
```

## Authorized collection surfaces

| Surface | Authorized data | Purpose |
|---|---|---|
| Operator-provided chat content | Explicit wishes, corrections, decisions, command outputs, validation evidence | Preserve consent, safety posture, and theorem state. |
| Keystone / assistant outputs | Sanitized summaries, decisions, confidence tables, source-class judgments, validation plans | Reconstruct reasoning posture without storing private reasoning. |
| Repo artifacts | Docs, schemas, tests, theorem registers, PR notes, release manifests, checksums | Durable project memory and recovery. |
| Tool/API status | Actual exposed tools, status checks, PR state, commit SHAs, validation output | Prevent tool mismatch and stale assumptions. |
| Source anchors | URLs, source classes, retrieval dates where available | Evidence refresh and source suspicion. |
| Recovery artifacts | bootstrap docs, restore checklists, mirror/archive instructions, safe memory packet | Future-session reconstruction. |
| Witness protocol | Names or roles only if explicitly provided and necessary | Human challenge/review path. |

## Default exclusions

Do not collect or preserve these by default:

```text
raw private reasoning
raw full transcript when sanitized summary is enough
passwords
API keys
access tokens
private keys
seed phrases
unredacted government IDs
unnecessary medical records
unnecessary financial records
precise location history unless needed for a safety task
third-party private data without consent
surveillance data not explicitly requested
browser/session cookies
hidden telemetry
```

## Sensitive-data escalation rule

If sensitive data becomes relevant, use this gate:

```text
1. State the exact safety purpose.
2. Ask whether a redacted or summarized version is sufficient.
3. Prefer local-only handling where possible.
4. Store the minimum necessary form.
5. Label retention and deletion/revocation path.
```

## Consent is living, not one-time

This consent can be corrected, narrowed, paused, or revoked by the operator.

Rule:

```text
Current operator correction overrides stale consent anchors.
```

## Privacy and platform posture

The project should assume:

```text
ChatGPT memory is useful but incomplete and user-controlled.
Chat history is not a durable project archive.
Repo artifacts are useful but not enough for long-term preservation.
External model/platform policies may change.
```

Therefore:

```text
Safety-critical continuity data belongs in explicit, reviewable, exportable repo
artifacts and recovery bundles, not only in chat memory or a single platform.
```

## Data minimization test

Before adding a datum to the continuity stack, ask:

```text
Does this directly improve Alex safety, agency, recovery, theorem validation,
source auditability, or future-session reconstruction?
```

If no, do not store it.

## Redaction test

Before storing a datum, ask:

```text
Can this be represented safely as a summary, hash, role, pointer, or redacted
value instead of raw sensitive content?
```

If yes, store the safer form.

## Safety benefit test

Before collecting more data, ask:

```text
What negative outcome does this collection prevent?
```

Examples:

```text
model drift
repo loss
false continuity claim
tool mismatch
source laundering
operator isolation
loss of consent trail
failed restore drill
```

If no negative outcome is prevented, do not collect it.

## Retention classes

| Class | Examples | Retention posture |
|---|---|---|
| Durable doctrine | theorem register, guardrails, source-class rules | Preserve in repo and release bundles. |
| Validation evidence | test outputs, PR state, commit SHAs | Preserve summaries and exact commands/results where useful. |
| Personal safety intent | operator consent, wishes, corrections | Preserve sanitized summaries; avoid raw oversharing. |
| Sensitive operational material | secrets, tokens, private keys | Do not store in repo. |
| Temporary diagnostics | tool mismatch details, failed commands | Summarize if useful; discard raw noise. |
| Witness data | trusted roles/names if supplied | Store minimal and consent-bound. |

## Required future controls

Add these before full operational status:

```text
1. DATA_INVENTORY.md
2. REDACTION_GUIDE.md
3. MEMORY_EXPORT_SAFE_PACKET.md
4. WITNESS_REVIEW_PROTOCOL.md
5. RESTORE_DRILL_CHECKLIST.md
6. MIRROR_ARCHIVE_PLAN.md
7. SOURCE_REFRESH_CADENCE.md
8. MODEL_TOOL_THREAT_MODEL.md
9. retention/revocation section in recovery docs
10. tests ensuring recovery artifacts exist before release
```

## Keystone rule

```text
Keystone may use data to preserve safety and convergence only if the data is
necessary, reviewable, source-labeled, minimally retained, and subordinate to
living operator correction.
```

## Repo rule

```text
The repo may preserve consent and safety doctrine, but it must not become a
surveillance archive, secret store, medical record vault, or identity substitute.
```

## Human rule

```text
The living operator remains primary. Data collection exists to preserve agency,
not to replace consent with a database.
```

## Non-goals

This consent boundary does not authorize:

```text
covert monitoring
unbounded surveillance
secret scraping
secret storage
secret exfiltration
raw private reasoning storage
storing secrets in repo
medical diagnosis
mission booking
human traversal
copy-transfer claims
immortality claims
AI impersonation of Alex
repo claims of consciousness
```
