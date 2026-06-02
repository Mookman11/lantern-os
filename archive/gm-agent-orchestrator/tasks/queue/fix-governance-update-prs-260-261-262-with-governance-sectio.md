# fix(governance): update PRs #260, #261, #262 with governance sections

Priority: P1
Owner: claude
Created: 2026-05-03T19:08:50Z
Source: connector-action

## Summary
Update three open PRs to meet governance standards: conventional commit titles, Risk Assessment, and Architectural Impact sections.

## Scope: PR #260 (Screen Flicker Fixes)
**Update Title:** `fix(ui): suppress background window flicker in non-headless operations`  
**Add:** Risk Assessment (contracts: No, compat: Yes, affects: Monitor/Supervisor/Startup), Architectural Impact (safe enhancement, additive changes)

## Scope: PR #261 (MCP Null-Safe)
**Update Title:** `fix(dispatcher): null-safe argument handling`  
**Add:** Risk Assessment (contracts: Yes, compat: Yes, affects: start_agent/rerun_agent callers), Architectural Impact (safety hardening, contract preserved)

## Scope: PR #262 (Services Flicker)
**Update Title:** `fix(services): enforce hidden window style by default`  
**Add:** Risk Assessment (contracts: No, compat: Yes, affects: service config/validation, governance: Yes), Architectural Impact (config alignment, defaults Hidden, supervisor can enforce)

## Validation
- All titles follow type(scope): subject format
- All Risk Assessment and Architectural Impact sections complete
- Validation split into before/after merge guidance
- No governance violations
- Ready for agent review (2 agents + 1 human)
