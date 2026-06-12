# MCP Work Split

Status: merged remote contract
Date: 2026-05-28

## Purpose

Split MCP and OS-review work into small lanes so the convergence fleet can review, validate, and hold work without making live-tool claims that are not yet proven.

## Split Lanes

| Lane | Purpose | Evidence required | Hold condition |
|---|---|---|---|
| Connector contract | Document the expected MCP connection path | `docs/MCP-CONNECTOR.md` and connector validation JSON | missing or stale connector doc |
| Connector probe | Check the actual visible MCP surface | current local probe output | local endpoint unavailable |
| Fleet count validation | Confirm designed counts and receipt shape | `CONVERGENCE-FLEET-LATEST.json` | no validator output |
| Runtime count report | Count real active workers | local orchestrator status report | cloud-only or metadata-only view |
| Tool descriptor review | Verify actual exposed tool names and parameters | captured tool descriptors | advertised-only tool list |
| RAG and memory routing | Route durable receipts into local memory indexes | generated manifests and hashes | private data or secrets present |
| OS issue review | Classify OS issues into fix, hold, reject, or promote | issue receipt with evidence and rollback | destructive, private, or physical action required |

## Private Dependency Boundary

The remote repository can store design contracts, validators, manifests, public-safe receipts, and claim boundaries. It cannot prove local-only MCP health, Windows process state, dirty worktree state, private folders, secrets, physical boot state, or live worker counts.

## OS Review Gate

Each OS issue review should return one classification:

- `fix`: safe repo/document/test change available now;
- `hold`: blocked by local runtime, account, physical action, payment, secret, or destructive operation;
- `reject`: conflicts with repo safety rules or evidence;
- `promote`: already validated and ready for operator review.

## No Bulk Remote Push Without Gate

Remote changes should stay small and reviewable. A batch may include related docs, scripts, and receipts only when they share the same validation path and no local-only state is being imported blindly.

## Ring Use Rule

When the 12x3 convergence ring is used for MCP work:

1. Step primary performs the lane review.
2. Backup A checks evidence and count completeness.
3. Backup B checks boundary and fallback.
4. The lane emits a receipt.
5. Live-tool or live-worker claims remain held until local proof exists.
