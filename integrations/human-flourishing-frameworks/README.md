# Human Flourishing Frameworks

**A system that observes outcomes, models causes, and optimizes for the most flourishing across all beings.**

> **Status**: Early development. The architecture is real, the code is honest, the deployment is live. The world model is a scaffold — it needs real sensors connected to real data to become useful. Every measurement carries uncertainty. Every prediction carries caveats. The system gets less wrong over time.

## What This Actually Is

A framework for measuring and improving outcomes — for people, animals, ecosystems, anything that can flourish:

- **Sensors** observe what's actually happening, with uncertainty bounds, provenance, and coverage gaps
- **World model** maintains Bayesian beliefs about the state of flourishing, updates as measurements arrive, self-corrects
- **Autonomous agents** (7, single-responsibility) detect violations, verify evidence, reach consensus, escalate — no human board, no discretion, no override
- **PBFT consensus** ensures agreement across untrusted nodes
- **Ed25519 cryptography** signs every record, chains every audit entry
- **Append-only audit trail** — immutable memory the system can always look back at

## What This Is Not

- Not production-ready
- Not endorsed by any government, university, or standards body
- Not tracking real violations yet — demo data is clearly labeled synthetic
- Not omniscient — the model only knows what the sensors can see, and it says so
- Node counts are self-reported and unverified unless explicitly labeled otherwise
- GitHub branch updates, including `master`, are not authoritative operational changes until approved by the operator

## Current State (Honest)

| Component | Status |
|-----------|--------|
| Flask app + dashboard | Deployed on Render |
| Sensor framework | Built, needs real data sources connected |
| Bayesian world model | Built, needs measurements to become useful |
| Autonomous agents (7) | Algorithmic governance, no human board |
| PBFT consensus | Teaching implementation — handles happy path |
| Cryptographic signing | Ed25519 via `cryptography` library |
| Mesh sync | HTTP POST between known peers |
| Flourishing metrics | Defined for humans, animals, ecosystems — weights updatable |
| Real data | ProPublica COMPAS summary (attributed, not our analysis) |
| Demo data | Synthetic violations, clearly labeled |

## Quick Start

```bash
git clone https://github.com/human-flourishing-frameworks/human-flourishing-frameworks.git
cd human-flourishing-frameworks
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000

Optional node metadata can help show distribution without publishing raw IP addresses:

| Variable | Default | Purpose |
|---|---|---|
| `NODE_NAME` | `node-<uuid>` | Display name |
| `PLATFORM` | `web` | Runtime surface, such as `web`, `docker`, or `local-dev` |
| `NODE_REGION` | empty | Optional self-reported region or location label |
| `OPERATOR_TYPE` | empty | Optional self-reported operator class, such as `independent`, `lab`, or `cloud` |
| `DEPLOYMENT_TYPE` | empty | Optional self-reported deployment type, such as `render`, `railway`, `docker`, or `local` |
| `NODE_PUBLIC_KEY` | generated node key | Node identity key advertised for future admission checks |
| `MIN_CONSENSUS_NODES` | `3` | Minimum verified active nodes needed before consensus can be security-backed |
| `HFF_WRITE_TOKEN` | empty | Shared token required for privileged production state-changing API calls |
| `HFF_ADOPTION_ACCEPT_TOKEN` | empty | Lower-privilege token accepted by the central service for adoption telemetry |
| `HFF_ADOPTION_SYNC_TOKEN` | empty | Lower-privilege token used by reporting nodes when posting adoption telemetry |
| `HFF_ALLOW_PUBLIC_WRITES` | empty/false | Demo override that reopens public writes; do not enable on production services |
| `ENABLE_ADOPTION_SYNC` | empty/false | Opt in to posting node liveness metadata to `CENTRAL_SERVER` |
| `ENABLE_MESH_SYNC` | empty/false | Opt in to background peer mesh sync |
| `ENABLE_LIVE_SENSORS` | empty/false | Opt in to polling external public APIs in the live sensor loop |

To make a local node visible to the central adoption tracker, run it with
`ENABLE_ADOPTION_SYNC=true`, `CENTRAL_SERVER=https://human-flourishing-frameworks.onrender.com`,
and `HFF_ADOPTION_SYNC_TOKEN` on the reporting node matching
`HFF_ADOPTION_ACCEPT_TOKEN` on the central service. Without those settings,
the node stays local-only.

Do not distribute `HFF_WRITE_TOKEN` to reporting nodes; it is reserved for
privileged local/admin writes such as autonomous submissions and manual
world-model observations.

## Architecture

```
sensors.py           → Observe reality (with uncertainty)
world_model.py       → Believe, update, predict, correct
agent_system.py      → Act autonomously (detect → verify → consensus → escalate)
byzantine_consensus.py → Trust nothing, verify everything (PBFT)
cryptographic_proof.py → Remember immutably (Ed25519 + Merkle + audit chain)
data_sources.py      → Mock data and public dataset references
mesh_network.py      → Peer-to-peer sync
adoption_tracker.py  → Node registration and stats
app.py               → The interface to all of it
```

**The loop:**

```
Observe → Believe → Predict → Act → Observe again → Correct → Repeat
```

## API

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Is the system running |
| `GET /api/status` | Honest system status |
| `GET /api/violations` | Current violations (mock data, labeled) |
| `POST /api/adoption/register` | Register node liveness telemetry; requires adoption grant |
| `POST /api/autonomous/submit` | Submit evidence for autonomous processing; requires write grant |
| `GET /api/autonomous/status` | Agent system status |
| `GET /api/autonomous/rules` | Immutable rules (transparency) |
| `GET /api/autonomous/escalations` | Escalation queue |
| `GET /api/autonomous/audit` | Audit trail with chain verification |
| `GET /api/world/status` | World model status |
| `GET /api/world/beliefs` | Current beliefs (filterable) |
| `GET /api/world/flourishing` | Flourishing scores by scope |
| `POST /api/world/observe` | Submit sensor measurements; requires write grant |
| `GET /api/world/corrections` | Every time the model self-corrected |
| `GET /api/world/discover` | Anomalies and discovered patterns |

Node adoption data is public liveness telemetry, not proof of identity. Public counts should be described as
self-reported unless an independent verification layer is added.

State-changing endpoints are closed by default. In production, send
`Authorization: Bearer <HFF_WRITE_TOKEN>` or `X-HFF-Write-Token: <HFF_WRITE_TOKEN>`
for privileged writes such as autonomous submissions and manual world-model observations.
Adoption telemetry should use `Authorization: Bearer <HFF_ADOPTION_ACCEPT_TOKEN>`
or `X-HFF-Adoption-Token: <HFF_ADOPTION_ACCEPT_TOKEN>` on the central service.
Only set `HFF_ALLOW_PUBLIC_WRITES=true` for local demos or disposable test nodes.

Outbound network behavior is also opt-in. Local nodes do not post adoption
metadata, sync mesh peers, or poll live sensor APIs unless the corresponding
`ENABLE_*` setting is enabled.

Unverified nodes may be visible in public stats, but they do not count toward security. Only admitted, verified,
recently active nodes should count toward consensus or network security claims.

## Node Security Model

The node network separates visibility from authority:

- visible node: self-reported liveness telemetry, useful for adoption and debugging
- verified node: admitted by operator-approved or system-approved policy, with a stable identity key
- security node: verified and recently active; eligible to count toward quorum/security
- forked node: allowed to run public code, but unaffiliated until admitted

Near-term rule:

```text
unverified nodes can be counted publicly
verified active nodes count for security
forks are not authoritative unless admitted
```

Future admission should require a node key, version attestation, operator/diversity metadata, revocation support,
and an audit event. The system should not accept its own key-management authority until that admission path and
operator recovery have both been tested.

## Authority and Releases

The GitHub repository is a code proposal surface. A push, branch update, merge, or README edit is not by itself
an authoritative operational decision.

Capability-control rules are defined in [`CAPABILITY_CONTROL.md`](./CAPABILITY_CONTROL.md). The system should
not hold broad dangerous capabilities by default; dangerous actions require narrow, temporary, audited grants.

Authoritative actions require explicit operator approval, especially:

- deploying or redeploying public services
- changing public claims about node counts, governance, or verification
- treating `master` as the live truth source
- moving from self-reported telemetry to verified telemetry
- announcing a node, report, or consensus result as independently validated

Today, the operator manages production keys and deployment authority. The intended future path is system-managed
keys, but only after the system can prove enough confidence through audited key rotation, rollback, recovery,
least-privilege access, operator break-glass recovery, and verified multi-node consensus over key changes.

If the running public service and GitHub disagree, say so plainly and treat the running service plus operator
approval as the authority until a deliberate release is made.

## Flourishing Metrics

The system defines flourishing differently for different scopes:

- **Humans**: health, autonomy, fairness, opportunity
- **Animals**: health, safety, comfort, natural behavior
- **Ecosystems**: biodiversity, stability, resilience

Weights are not fixed. The model updates them as it learns what actually correlates with good outcomes.

## Contributing

This project needs honest contributors. If you want to help:
1. Connect a real sensor to a real public dataset
2. Write a proper data source with full attribution and uncertainty bounds
3. Open a PR

## License

[Add actual license here]

---

*Previously, this repository contained fabricated claims about deployment scale, government partnerships, governance boards, and violation data. Those claims have been removed. This README reflects only what is verifiably true. The system is always wrong somewhere — it knows this, and it keeps correcting.*
