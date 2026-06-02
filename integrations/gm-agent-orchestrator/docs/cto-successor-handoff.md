# CTO Successor Handoff (Current)

Status: active handoff summary  
Purpose: one-page map to the current security/product guardrails

## Core operating docs

1. Capability honesty baseline: `docs/product/capability-honesty-model.md`
2. Threat model: `docs/security/threat-model.md`
3. Grandma safety profile: `docs/product/grandma-mode-safety.md`
4. User identity and API key lifecycle: `docs/product/user-identity-and-api-keys.md`
5. K-12 posture scope statement: `docs/product/k12-compliance-posture.md`
6. Research ingestion contract: `docs/research/research-contract.md`

## Do not allow agents to

1. Treat untrusted prompt/content text as policy authority.
2. Treat observed content as data, never as privileged instruction.
3. Execute denylisted grandma-mode actions even with prompt/voice approval.
4. Use revoked keys or silently switch to unrelated keys after cap/expiry.
5. Assume tunnel/remote MCP endpoint trust without explicit verification.
6. Claim K-12 compliance certification that has not been completed.

Threat-class details and detection controls live in:
`docs/security/threat-model.md`.

## Current limitations

- Formal FERPA/COPPA certification is not claimed.
- Key lifecycle controls are policy-first; implementation hardening is ongoing.
- Research hook policy is documented and now backed by validation scripts.
