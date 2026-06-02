# Seven-Step Dashboard Convergence Strategy

Status: strategy artifact for issue #73.

## Purpose

This document turns current dashboard and deployment doubts into a seven-step,
testable strategy. It keeps public visibility honest without broadening runtime
authority, enabling sensors, exposing secrets, or rewriting the dashboard blindly.

## Current doubts

| Doubt | Why it matters | Current confidence |
|---|---|---:|
| Dashboard may fail silently when safe-read APIs fail. | Blank/stale public UI can create false confidence. | 70 |
| `/healthz` is referenced as desirable but not yet verified. | Deploy platforms and humans need a lightweight readiness check. | 75 |
| Live deployment health is not proven by docs or CI. | Public claims need fresh smoke evidence. | 90 |
| Dashboard language may still look more authoritative than intended. | Public UI should remain advisory/research, not authority. | 65 |
| Large embedded template makes blind edits risky. | Full-file rewrites can regress unrelated UI. | 95 |
| Accessibility is policy-level, not implementation-level. | Public usefulness needs more than docs. | 80 |
| Deployment checks should not expose operational security details. | Safe teaching and smoke checks must remain harmless/read-only. | 90 |

## The seven steps

| Step | Strategy | Dashboard application | Pass condition |
|---:|---|---|---|
| 1 | Say the claim. | The dashboard is public advisory research UI and should show current safe-read status honestly. | Claim appears in issue/PR text and, where appropriate, UI copy. |
| 2 | Set the guard. | No secrets, no public writes, no sensor enablement, no mesh enablement, no actuator/control behavior. | Patch touches only route/UI/test surfaces needed for health/degraded-state visibility. |
| 3 | Add the tiny check. | Add tests for `GET /`, `GET /health`, `GET /healthz`, and advisory dashboard language. | Local/CI unittest fails if routes or boundary text disappear. |
| 4 | Try safely. | Run Flask client tests and CI before deploy; use read-only smoke checks after deploy. | Tests pass without credentials or private endpoints. |
| 5 | Look at reality. | Compare README/policy claims to actual route responses and deployed smoke evidence. | Public `curl -i` evidence matches documented routes/status. |
| 6 | Fix the mismatch. | If dashboard/API/deploy disagree, update the smallest wrong layer: docs, test, app route, or deploy config. | The correction is narrow and evidence-backed. |
| 7 | Repeat later. | Keep route and public-boundary checks in CI; re-smoke after deployment changes. | Future PRs cannot silently remove health/degraded-state guardrails. |

## Best next implementation slice

| Order | Change | Why this first |
|---:|---|---|
| 1 | Add Flask client tests for public health/dashboard routes. | Establish expected behavior before modifying the app. |
| 2 | Add or verify `/healthz` as lightweight JSON. | Low-risk deployment readiness improvement. |
| 3 | Add visible degraded-state UI text for failed safe-read API calls. | Avoid silent public failures. |
| 4 | Add dashboard advisory-language assertion. | Prevent public authority drift. |
| 5 | Wire dashboard health tests into CI. | Make regression detection automatic. |
| 6 | Deploy deliberately. | Runtime truth changes only after reviewed merge/deploy. |
| 7 | Capture smoke evidence. | Public deployment confidence comes from observed responses, not repo state alone. |

## Child-safe public teaching version

For non-technical public explanation, avoid security mechanics and use:

```text
I have an idea.
I make it kind.
I check one tiny part.
I try it where nobody gets hurt.
I look and listen.
I fix the wobbly part.
I try again tomorrow.
```

This maps to the engineering process without exposing secrets, attack paths,
credentials, hidden endpoints, private logs, or physical control mechanisms.

## Not in scope

- live sensor enablement;
- mesh sync enablement;
- public writes;
- token or credential changes;
- deployment credential handling;
- SDK/APK work;
- vehicle/device control;
- broad dashboard redesign;
- private diagnostics or internal logs in public UI.

## Merge gate for dashboard fixes

A future dashboard-fix PR should not merge unless:

| Gate | Required evidence |
|---|---|
| Route tests | `GET /`, `GET /health`, and `GET /healthz` pass under Flask test client. |
| Public status | `GET /api/status` is tested if the route exists. |
| UI boundary | Dashboard text remains advisory/research, not authority. |
| Degraded state | Safe-read API failure has visible user-facing fallback. |
| CI | Relevant tests pass in GitHub Actions. |
| Runtime boundary | No public writes/sensors/mesh/actuators are enabled by the patch. |
| Deployment evidence | After deploy, public smoke checks are captured before claiming live health. |

## Confidence after this strategy

| Area | Confidence |
|---|---:|
| Problem clarity | 93 |
| Safe next-step clarity | 95 |
| Dashboard runtime confidence | 58 |
| Live deployment health confidence | 45 |
| Avoiding dangerous exposure | 92 |
| Near-best path identified | 90 |

## Boundary

This strategy does not claim the dashboard is fixed. It defines the safe path to
fix it: tests first, tiny route/UI changes, CI, then live read-only smoke evidence.
