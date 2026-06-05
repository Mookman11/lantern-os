# Security Policy

Lantern OS is a private, local-first workspace. Treat local state as sensitive:
journal data, RAG records, runtime receipts, secrets, tokens, operator notes,
and private test artifacts must not be committed or shared publicly.

## Reporting Security Issues

Do not open public issues for secrets, authentication bypasses, private data
exposure, unsafe remote dispatch, tunnel exposure, or local MCP/tooling leaks.

Use a private channel with the repository owner and include:

- A short description of the issue.
- The affected file, service, route, or workflow.
- Reproduction steps, if safe to share.
- Whether the issue was locally verified.
- Any redacted evidence paths or logs.

## Local-First Verification

Before trusting a remote endpoint, tunnel, mirrored surface, or advertised tool
catalog, verify the local source of truth:

- Git state and dirty worktree risk.
- Local service health.
- Actual exposed MCP tools.
- Queue, task, and log state when dispatch is involved.

## Secret Handling

- Keep real secrets in ignored local environment files or a secret manager.
- Commit only safe examples such as `.env.example`.
- Rotate any secret that appears in Git history, logs, screenshots, or public
  surfaces.
