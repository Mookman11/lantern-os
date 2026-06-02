# test(governance): validate PR governance alignment

Priority: P1
Owner: gemini
Created: 2026-05-03T19:08:54Z
Source: connector-action

## Summary
Validate that PR updates and governance templates align with ADR-001 and drift-prevention-contract.md.

## Validation Checklist
- [ ] PR template enforces all sections (Summary, Changes, Risk, Architectural Impact, Validation, Related Issues)
- [ ] All three PR titles follow conventional commit (type(scope): subject)
- [ ] All scopes are specific (dispatcher, services, ui â€” not vague)
- [ ] Risk Assessment sections complete (contracts, compat, affects, governance)
- [ ] Architectural Impact sections explain boundaries
- [ ] Validation split into before/after merge
- [ ] All PRs link to related issues/ADRs
- [ ] No contradictions with governance framework

## Output
Create `reports/governance-validation-2026-05-03.md`:
- Pass/Fail summary
- Issues found (if any)
- Recommendation: Ready for human review?

## Related
- ADR-001 (enforcement)
- drift-prevention-contract.md (governance)
- RC3 Phase 1 readiness
