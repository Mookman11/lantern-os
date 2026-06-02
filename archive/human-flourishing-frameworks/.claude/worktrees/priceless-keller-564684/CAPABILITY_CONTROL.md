# Capability Control

The system must be unable to perform dangerous actions by default.

This is stronger than asking an agent to be careful. The default runtime should
observe, explain, simulate, and propose. It should not hold broad credentials
that allow irreversible external changes.

## Default Capabilities

Allowed by default:

- read public status
- read local health
- explain current state
- simulate proposed changes
- write local drafts
- propose releases, node admissions, and key changes

Not allowed by default:

- push to GitHub
- deploy or redeploy public services
- rotate, export, or replace production keys
- mark a node verified
- treat a fork as official
- treat `master` or any branch as operational authority
- announce consensus/security claims as independently validated

## Grants

Dangerous actions require explicit, narrow, temporary grants.

Each grant should name:

- action type
- exact target
- approving authority
- expiration
- rollback path
- audit record location

Examples:

```text
commit_grant: commit staged local source changes
push_grant: push commit 17bc948 to origin/master
deploy_grant: deploy exact commit SHA to Render
node_admission_grant: mark node public key X as verified
key_ceremony_grant: rotate key Y after recovery test Z
repo_retirement_grant: archive/remove GitHub only after signed release recovery works
```

## Key Authority

Today, the operator manages production keys and deploy authority.

The system may not become the sole key manager until these gates pass:

- operator recovery key exists
- offline backup or recovery shard exists
- key rotation is audited
- rollback is tested
- break-glass recovery is documented and tested
- at least two independent verified nodes can validate a key change
- key changes create signed audit events

## Node Authority

Public nodes are visible telemetry only.

Verified nodes are admitted nodes with stable identity keys. Only verified,
recently active nodes may count toward consensus or security claims.

Forks may run the public code, but they are unaffiliated unless admitted by a
signed membership record.

## GitHub Authority

GitHub is a code proposal surface, not the operational authority.

A branch update, merge, or push is not authoritative until an approved release
or deploy grant says so. If GitHub and the running service disagree, report the
disagreement plainly.

## Required Stop Points

The system must stop and request a grant before:

- merging when remote has changed unexpectedly
- pushing to a protected or deploy-linked branch
- triggering a deploy
- changing public claims about nodes, governance, verification, or consensus
- admitting a node as verified
- rotating or replacing keys
- retiring the repository

## Production Write Surface

HTTP endpoints that mutate node state, world-model state, or autonomous
escalation state must be closed by default.

Production writes require either:

- a narrow bearer/API token grant for the exact service
- a future signed node-admission or signed sensor-admission protocol

`HFF_ALLOW_PUBLIC_WRITES=true` is a demo override only. It must not be enabled
on an authoritative public service.

Outbound sync is also opt-in. Adoption telemetry, mesh sync, and live sensor
polling should require explicit runtime settings so local nodes do not contact
public services or peers just by starting the app.
