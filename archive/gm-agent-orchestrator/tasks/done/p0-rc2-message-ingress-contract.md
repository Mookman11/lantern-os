# P0 RC2 Message Ingress Contract

role_owner: gpt  
fallback_owner: human  
risk_class: medium  
budget_class: light  
terminal_rule: done|failed|requeued|blocked

## Objective

Define the auditable message-ingress contract that turns operator intent into orchestration actions while preserving dry-run-first mutation safety.

## Scope

- Define canonical intake schema and classification states.
- Define `requiresMutation` and `requiresDryRun` gating semantics.
- Define required response envelope for operator-safe feedback.
- Do not implement broad UI redesign or framework migration.

## Required Deliverables

1. In-repo contract update for message schema and classification state machine.
2. Explicit list of inline-safe vs queue-required message classes.
3. Dry-run card contract for all mutation-capable intents.
4. Audit event requirements for each ingress stage.

## Execution Gates

1. `tasks/active` must be empty before dispatch.
2. Any change must preserve `/dashboard` as canonical route.
3. No direct mutation action may be enabled from raw prompt input.

## Validation Commands

```powershell
git status --short
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-OrchestratorStatusJson.ps1 -Root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Test-OrchMcpServerContracts.ps1 -Root .
```

## Evidence Required

- Commands run and exit status.
- File paths updated for ingress contract.
- One example intent classification and resulting dry-run gating decision.
- One next action.

## Terminal Criteria

- `done`: contract is documented and validated, with evidence.
- `failed|blocked`: missing contract sections or failing validations with blocker note.
- `requeued`: partial output with explicit remaining gap and safe restart step.
