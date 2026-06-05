# Support

Lantern OS support starts from verified local state. When asking for help or
handing work to another agent, include evidence instead of assumptions.

## Useful Context

- Current branch and dirty worktree summary.
- The exact command, route, script, or workflow that failed.
- Local service URL and health result, if applicable.
- Relevant MCP tool list or mismatch, if applicable.
- Recent logs or receipts, redacted when needed.
- Whether the problem affects runtime behavior, docs, tests, or release
  packaging.

## Preferred Validation

Use the narrowest check that proves the change:

```bash
npm run check
npm run test:api
npm run test:chat
npm run test:ui
npm run validate
```

For Python-specific changes:

```bash
python -m pytest tests -q --tb=short
```

## Boundaries

Do not move queued work, start agents, sync repositories, reset branches, clean
the working tree, or trust remote tunnels without explicit evidence and intent.
