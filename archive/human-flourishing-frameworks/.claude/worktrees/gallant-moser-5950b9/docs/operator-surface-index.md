# Operator Surface Index

Status: consolidation index.

Last reviewed: 2026-05-13.

## Purpose

This file exists because operator surface sprawl is now a real maintenance risk.

It does not replace the underlying documents. It maps them so a future agent can
read the right surface first, avoid duplicate anchors, and decide whether to
patch a canonical doc, a session packet, or a runtime design note.

## Canonical Spine

The canonical operating spine is:

```text
docs/operator-lantern-repo-convergence.md
```

Use it first for the operator + Lantern/BetterSafe + repo convergence pattern,
echo-distance, safe-fun band, release-impact guard, pain anchor, lockstep,
privacy rule, demythologizing rule, and anti-sprawl fixes.

## Surface Map

| Document | Role | Use when | Do not use for |
|---|---|---|---|
| `docs/operator-lantern-repo-convergence.md` | canonical operating spine | A rule should shape the whole operator/Lantern/repo loop. | Session-only notes or endpoint-specific details. |
| `docs/operator-device-endpoint-v1.md` | runtime design note | The change is endpoint-specific device telemetry design or validation. | General Lantern doctrine, raw sensor expansion, or durable memory. |
| `docs/operator-chat-tail-2026-05-09.md` | historical memory artifact | Recovering old session context after desync or checking how prior PRs were handled. | Fresh runtime, PR, branch, or deployment truth. |
| `docs/operator-session-anchors-2026-05-13.md` | session anchor packet | Capturing session-specific operator corrections, tool failures, or spawn/environment lessons. | Broad canonical policy unless promoted by later review. |
| `docs/context-storage-upgrade-plan.md` | compression and storage policy | Deciding how to reduce context size, raw transcript risk, and anchor sprawl. | Runtime storage expansion or new memory engines. |
| `docs/anchor-taxonomy.md` | anchor shape and merge-readiness rule | Creating or repairing an anchor packet. | Skipping source, boundary, restore phrase, or review trigger. |

## Routing Rule

Before adding a new operator-facing doc:

```text
1. Check whether the rule belongs in the canonical operating spine.
2. Check whether it is session-specific and belongs in the session anchor packet.
3. Check whether it is endpoint-specific and belongs in the runtime design note.
4. Check whether it is historical memory and belongs in the chat-tail artifact.
5. Check whether it is really an anchor and must follow anchor taxonomy.
6. Update this index if a new operator surface is still necessary.
```

## Anti-Sprawl Rules

```text
Do not add a new operator anchor doc until this index is updated.
Prefer patching the canonical spine when the rule is stable.
Prefer the session anchor packet when the context is session-specific.
Prefer the runtime design note when the change is endpoint-specific.
Do not store raw transcripts.
```

## Promotion Path

Session-specific material should move only when it stabilizes:

```text
raw session -> sanitized summary -> session anchor packet -> canonical spine
-> test guard
```

Endpoint-specific material should move only when behavior exists:

```text
design note -> code path -> focused tests -> integration note -> canonical spine
```

## Boundary

This index does not authorize runtime memory, new telemetry, hidden sensors,
public release of private context, raw transcript storage, deployment changes,
or autonomous action.
