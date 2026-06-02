# P0 RC2 Policy Routing Contract

role_owner: gpt  
fallback_owner: human  
risk_class: high  
budget_class: medium  
terminal_rule: done|failed|requeued|blocked

## Objective

Codify deterministic routing policy with explicit allow/deny/needs_approval behavior and a fallback chain that avoids unsafe autonomous dispatch.

## Scope

- Define routing decision inputs and outputs.
- Define hard policy overrides for classifier suggestions.
- Define fallback chain (`gpt -> codex -> claude -> human_review`) with gates.
- Define refusal and blocker payload shape.

## Required Deliverables

1. Routing decision contract document update.
2. Required task metadata list enforced by policy.
3. Deny and needs-approval rules for risky and destructive requests.
4. Sticky auditable approval rule for Codex tasks (scope + TTL + approval reference).

## Execution Gates

1. No routing that bypasses queue lifecycle for mutating work.
2. No Codex dispatch without valid approval record.
3. No Claude fallback dispatch unless wake-safe preflight passes.

## Validation Commands

```powershell
git status --short
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-LocalRouterPolicy.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-AgentRoutingMap.ps1 -Root .
```

## Evidence Required

- Command evidence and pass/fail.
- At least three example route decisions:
  - allowed
  - needs_approval
  - blocked
- One next action.

## Terminal Criteria

- `done`: policy contract is decision-complete and tests pass.
- `failed|blocked`: unresolved policy gap or failing tests with blocker evidence.
- `requeued`: partial contract with exact unresolved section and handoff.
