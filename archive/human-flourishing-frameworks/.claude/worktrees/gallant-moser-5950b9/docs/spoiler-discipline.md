# Spoiler Discipline

Status: governance/guardrail artifact.

## Anchor

```text
Reveal enough to help. Hold enough to protect.
```

## Purpose

Spoiler discipline defines how HFF handles information that may be true, useful,
interesting, or meaningful but should not be revealed too early, too broadly, or
without the right consent and context.

A spoiler is not only a story ending. In HFF, a spoiler can be:

- a security detail that creates misuse risk;
- a private human detail shared without consent;
- an operational mechanism that should remain internal;
- a future claim presented before evidence exists;
- a symbolic meaning forced onto someone before they choose it;
- or a conclusion shown before the tests and limits are visible.

## Seven-step spoiler method

| Step | Spoiler application | Pass condition |
|---:|---|---|
| 1. Say the claim | Identify what might be revealed. | The claim is named before sharing. |
| 2. Set the guard | Decide who could be harmed or misled by disclosure. | Secrets, private data, exploit paths, and premature certainty are blocked. |
| 3. Add the tiny check | Ask whether the audience needs the detail now. | Detail is necessary, consented, and safe. |
| 4. Try safely | Share the least dangerous useful version first. | Public copy uses summaries, boundaries, and redactions. |
| 5. Look at reality | Watch for misunderstanding or overclaim. | Corrections are accepted quickly. |
| 6. Fix the mismatch | Redact, clarify, or downgrade confidence. | Public record no longer overexposes or overclaims. |
| 7. Repeat later | Reassess as context changes. | More detail is revealed only when safer and justified. |

## Reveal / hold table

| Reveal | Hold |
|---|---|
| Public boundaries | Secrets, tokens, credentials |
| Health/status summaries | Private logs and stack traces with sensitive data |
| General safety method | Exploit paths or bypass details |
| Confidence and uncertainty | False certainty or unsupported proof claims |
| Consent principles | Private details about real people |
| Source classes | Unreviewed private/raw sources |
| Release gates | Deployment credentials or hidden endpoints |
| Anchors | Dangerous mechanisms or control instructions |

## Spoiler types

| Type | Risk | Safe handling |
|---|---|---|
| Story spoiler | Ruins discovery or surprise. | Ask or warn before revealing. |
| Security spoiler | Enables misuse. | Keep operational details private; publish principles only. |
| Privacy spoiler | Pulls a person into a narrative. | Get direct consent or omit. |
| Emotional spoiler | Forces meaning too early. | Offer gentle framing, not imposed interpretation. |
| Future spoiler | Treats possibility as already true. | Label speculation and evidence gaps. |
| Convergence spoiler | Skips tests and jumps to conclusion. | Show method, limits, and confidence. |
| Authority spoiler | Makes evidence sound like permission to act. | Say the boundary explicitly. |

## Public release rule

Public HFF copy should be transparent enough for trust and safety, but not so
specific that it exposes private people, secrets, exploit paths, operational
bypass details, or unsupported future claims.

```text
Transparency is not total exposure.
Privacy is not secrecy-as-power.
Safety is revealing the right thing at the right level.
```

## Examples

| Context | Better public wording | Do not reveal |
|---|---|---|
| Dashboard health | `Some dashboard data is unavailable; check /healthz.` | Private deployment logs with secrets. |
| Sensors | `9 registered sensors; no successful observation cycle reported yet.` | Personal telemetry or hidden identifiers. |
| Security posture | `Public writes are disabled by default.` | Token formats, bypasses, or attack recipes. |
| People nearby | `A friend is present and privacy is respected.` | Names/details unless they directly consent. |
| Future claims | `This is a possibility, not a demonstrated capability.` | Certainty or proof language without evidence. |

## Boundary

Spoiler discipline does not hide failures to protect ego. It protects people,
security, consent, and epistemic honesty. Failures that affect public trust should
be disclosed at a safe level with clear corrections and without dangerous detail.