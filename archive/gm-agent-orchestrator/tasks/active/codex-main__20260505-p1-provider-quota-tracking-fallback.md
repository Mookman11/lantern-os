# Task: Provider quota tracking and fallback routing (#259 Phase 1.2)

Priority: P1
Owner: codex (implementation) + claude (review)
Estimated time: 2 hours
Depends on: #256 MCP dispatch fix (headless null-safe)
Blocks: multi-slot sustained operation

## Context

RC3 tracker #259 Phase 1.2. Without quota tracking, the orchestrator blindly
retries a rate-limited provider until a human notices. The fallback map
(Claude → Codex → Gemini → GPT-Web) exists as a doc but is not enforced by code.

## Scope

### New: `status/quota-tracker.json`

Schema:
```json
{
  "updatedAt": "<iso>",
  "providers": {
    "claude":  { "state": "ok|limited|unknown", "resetAt": null, "failCount": 0 },
    "codex":   { "state": "ok|limited|unknown", "resetAt": null, "failCount": 0 },
    "gemini":  { "state": "ok|limited|unknown", "resetAt": null, "failCount": 0 },
    "gpt-web": { "state": "ok|limited|unknown", "resetAt": null, "failCount": 0 }
  },
  "fallbackOrder": ["claude", "codex", "gemini", "gpt-web"]
}
```

### Edit: `scripts/Invoke-OrchestratorAgentAction.ps1`

- After a dispatch failure that matches quota/rate-limit error patterns, increment
  `failCount` and set `state: limited` for that provider in `status/quota-tracker.json`.
- On next dispatch request for a limited provider, consult `fallbackOrder` and
  route to the next available provider.
- Do not silently swallow errors  -  surface the reroute decision in the slot log.

### Edit: `scripts/Start-AgentSlot.ps1`

- On resume loop: check `status/quota-tracker.json` before retrying.
- If provider is `limited` and `resetAt` is in the future, sleep until `resetAt`
  rather than the hardcoded `fallbackWaitMinutes`.

### New: `tests/Test-QuotaTracker.ps1`

- Validate schema, state transitions, and fallback order.

## Done criteria

- `status/quota-tracker.json` is written/updated by Invoke-OrchestratorAgentAction.
- Fallback provider is selected when primary is `limited`.
- Reroute decision is logged to the slot log.
- `Test-QuotaTracker.ps1` passes.
- `Test-PowerShellSyntax.ps1` passes on all changed files.
- Branch pushed, PR open.

## Reference

- Issue: #259 Phase 1.2, #224
- Capacity limits: `docs/suzie-provider-capacity-limits.md`
- Fallback design: `docs/agents/local-routing-policy.md`
