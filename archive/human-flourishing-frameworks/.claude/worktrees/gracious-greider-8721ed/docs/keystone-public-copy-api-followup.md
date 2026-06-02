# Keystone Public-Copy Incident — API Surface Follow-up

Status: durable follow-up to the public-copy incident memory.

Last reviewed: 2026-05-09.

This note records a follow-up lap of the public-copy incident: after the HTML
dashboard was sanitized, live evidence showed that the public JSON API
continued to expose the same authority semantics under the same names. The fix
shipped on this lap is a source-level public projection helper. This note
records what the immutables are after the fix, what changed, and what stayed
the same.

It is intentionally docs-only. It adds no runtime memory engine, polling,
autonomous behavior, deployment hook, secret access, or mesh write.

## Finding

Live evidence captured 2026-05-09 ~15:17 UTC against
`https://human-flourishing-frameworks.onrender.com/api/autonomous/status`
showed:

```text
auto_execute_escalations_enabled: false   # gated correctly
public_writes_enabled: false              # gated correctly
mesh_sync_enabled: false                  # gated correctly
data_source: mock                         # honest
mode: research                            # honest

immutable_rules.no_human_override: true                  # unsafe
immutable_rules.escalation_is_irreversible: true         # unsafe
immutable_rules.escalation_lock_hours: 24                # real behavior
```

The HTML cleanup (`safe_app.py` + `e61eb08` source fix) removed the unsafe
authority phrases from the dashboard page. The JSON API was outside that
bundle and continued to expose the same authority claims structurally:

```text
"no_human_override: true"           ≡  "No human board"
"escalation_is_irreversible: true" + "escalation_lock_hours: 24"
                                    ≡  "irreversible after a 24-hour lock"
```

Per the public-copy incident memory's own learned rule:

```text
One public-copy incident must be handled as a bundle:
source, startup paths, tests, deploy target, live validation, and outreach.
```

The API surface was the missing leg of the bundle.

## Engineering reality

Closer reading of `agent_system.py` showed the two flag-style fields are
descriptive metadata, not enforcement mechanisms:

```text
no_human_override            asserted == True at AgentBase init; never checked
                             to refuse an override request
escalation_is_irreversible   only logged as audit metadata; SQLite append-only
                             design carries the real irreversibility property
```

The actual behavioral guards are:

```text
auto_execute_escalations_enabled   environment-flag gated, defaults False
escalation_lock_hours              real numeric value used in lock math
SQLite append-only schema          real irreversibility at the storage layer
operator/deployment authority      external to the software
```

So the right fix was a public projection of the rules, not a runtime change.
Internal `IMMUTABLE_RULES` constant unchanged. No autonomy enablement. No mesh
writes. No PR #20 territory crossed.

## What the immutables are after the fix

Internal `IMMUTABLE_RULES` constant in `agent_system.py` (unchanged, all 7
fields kept so `AgentBase._validate_rules` startup assertions still pass):

```python
IMMUTABLE_RULES = {
    "accuracy_gap_threshold": 0.05,
    "escalation_lock_hours": 24,
    "escalation_is_irreversible": True,
    "no_human_override": True,
    "consensus_threshold_formula": "quorum_size(n) / n  # i.e. (2f+1)/n from PBFT",
    "agent_count": 7,
    "append_only_audit": True,
}
```

Public projection returned by `public_immutable_rules_view()` and exposed via
`/api/autonomous/status`, `/api/autonomous/rules`, and the startup audit log
entry:

```python
{
    "accuracy_gap_threshold": 0.05,
    "escalation_lock_hours": 24,
    "consensus_threshold_formula": "quorum_size(n) / n  # i.e. (2f+1)/n from PBFT",
    "agent_count": 7,
    "append_only_audit": True,
    "mode": "research",
    "disclaimer": "Research advisory software. Operator and deployment "
                  "authority are external to this system. Escalation records "
                  "are audit-log entries pending human review, not regulatory "
                  "actions or autonomous enforcement.",
}
```

Two fields are intentionally absent from the public view:

| Field | Why omitted from public |
|---|---|
| `no_human_override` | Self-asserted at startup but never used to refuse override; field name implies governance authority the software does not possess |
| `escalation_is_irreversible` | Only carried as audit metadata; the real append-only property is enforced by SQLite, not by this flag |

The omission list is encoded in `_INTERNAL_ONLY_RULE_KEYS` and guarded by the
`tests/test_safe_public_api_copy.py` regression test.

## What changed in source

| File | Change |
|---|---|
| `agent_system.py` | Added `public_immutable_rules_view`, `_INTERNAL_ONLY_RULE_KEYS`, `PUBLIC_RULES_DISCLAIMER`. Wired projection through `get_status`, `get_rules`, and the startup audit log entry. Removed `irreversible` field from the `escalation_locked` audit detail. Reframed module docstring (no more "Governance flow is algorithmic"). |
| `app.py` | Updated `/api/autonomous/rules` route docstring to describe the public projection. |
| `tests/test_safe_public_api_copy.py` | New regression test (6 cases) asserting the public view omits the forbidden keys and serializes without the forbidden phrases, while keeping internal `IMMUTABLE_RULES` intact. |
| `scripts/validate_public_site.ps1` | Now also fetches `/api/autonomous/status` and `/api/autonomous/rules` and asserts forbidden phrases absent from the JSON. |

## What stayed the same

```text
runtime behavior of the autonomous system
auto_execute_escalations_enabled gating
SQLite append-only escalation table
PBFT consensus math
24-hour lock period (escalation_lock_hours)
violation detection threshold (accuracy_gap_threshold)
AgentBase._validate_rules startup assertions
PR #20 status (open/draft, held)
deployment target (Render)
secrets, tokens, environment variables
```

## Verification

```text
python -m unittest discover -s tests   ->  104 tests, OK
                                            (6 new + 98 prior)
```

Live verification of the deployed result is deferred until the source change
reaches Render. The widened smoke validator now encodes a stricter contract
than what the currently-deployed service serves; it will pass after Render
redeploys with these commits.

## Confidence table

| Claim | Confidence |
|---|---:|
| The pre-fix public API exposed authority semantics structurally identical to the cleaned HTML | 0.99 |
| The flag-style fields were descriptive metadata, not enforcement | 0.97 |
| The public projection is the right fix shape (mirrors the prior HTML source cleanup) | 0.95 |
| Runtime behavior is unchanged by the fix | 0.97 |
| The widened smoke validator catches the regression class going forward | 0.92 |
| Live deployed result will pass the new smoke contract after Render redeploys | 0.85 |

## Merge boundary

This follow-up lap is on the allowed side of the public-copy incident memory's
merge boundary:

```text
copy/source fix       (public projection helper)
regression test       (tests/test_safe_public_api_copy.py)
validation script     (scripts/validate_public_site.ps1 widening)
docs-only memory      (this file)
```

It does not touch the blocked side:

```text
no PR #20 merge
no autonomous executor enablement
no mesh write expansion
no autonomy claim without endpoint evidence
no raw chat transcript commit
no model-sent outreach
no env var or secret change
no Render redeploy by Keystone
```

## Non-goals

```text
runtime memory engine
chat transcript ingestion
new endpoint surface
new autonomy
new live polling
new deployment target
public scoring of people
moral authority claims
```
