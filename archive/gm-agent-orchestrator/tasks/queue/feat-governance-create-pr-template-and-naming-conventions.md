# feat(governance): create PR template and naming conventions

Priority: P1
Owner: codex
Created: 2026-05-03T19:08:24Z
Source: connector-action

## Summary
Create enforcement templates for all future PRs to ensure governance standards are met automatically, not manually.

## Scope
1. Create `.github/PULL_REQUEST_TEMPLATE.md` â€” Single source of truth for PR structure
   - Mandatory sections: Summary, Changes, Risk Assessment, Architectural Impact, Validation (before/after), Related Issues
   - Examples of good/bad content
   - Enforcement: Template blocks incomplete PRs

2. Create `docs/PR-NAMING-CONVENTIONS.md` â€” Reference standard for titles
   - Convention: type(scope): subject (conventional commits)
   - Specific scopes: dispatcher, services, monitor, ui, startup, queue, governance, docs
   - Examples: good vs. bad titles
   - Why it matters: grepability, audit trail, governance alignment

## Files to Create
- `.github/PULL_REQUEST_TEMPLATE.md` (enforce structure)
- `docs/PR-NAMING-CONVENTIONS.md` (reference guide)

## Validation
- Template renders in GitHub PR creation flow
- Naming doc is discoverable and comprehensive
- Both docs follow repo conventions (markdown, clear formatting, examples)

## Related Issues
- ADR-001 (enforcement architecture)
- drift-prevention-contract.md (governance)
- RC3 roadmap Phase 1 preparation

## Why This First
Templates must exist before PRs are updated. This unblocks all downstream work.

## Success Criteria
- âœ… Files created and committed to master
- âœ… PR template enforces all required sections
- âœ… Naming conventions documented with clear examples
- âœ… Ready for PRs #260, #261, #262 to be updated
