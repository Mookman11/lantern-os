# Human Flourishing Frameworks

**An experimental advisory and orchestration framework for source-backed modeling, safety boundaries, and human-flourishing system design.**

> **Status:** early development experimental software. The public service is live, but it is not production authority infrastructure. Measurements carry uncertainty, node counts are self-reported unless explicitly verified, and GitHub changes are code proposals until deliberately deployed and validated.

## Current deployment

Primary cloud URL:

```text
https://web-production-46794.up.railway.app/
```

Health/status checks:

```bash
curl -i https://web-production-46794.up.railway.app/health
curl -i https://web-production-46794.up.railway.app/api/status
```

The container is started with gunicorn and binds to Railway's injected `PORT`, falling back to `5000` for local Docker runs.

Render may appear in older logs or historical deploys, but Railway is the current public deployment target being validated here.

## Capability and authority boundary

HFF can do more than passive research, but capability is not authority.

HFF can help:

- model sources, uncertainty, evidence, risks, and candidate actions;
- run bounded local or deployment-support workflows when explicitly enabled;
- support operator-reviewed decisions with logs, tests, and audit evidence;
- expose status, beliefs, synthetic demos, and advisory results;
- test safety boundaries, release posture, and system convergence.

HFF does not have public authority over people, communities, institutions, or living systems.

Public-facing use should remain:

```text
source-backed
uncertainty-aware
operator-reviewed
bounded by explicit grants
challengeable
rollback-aware
advisory by default
```

The system must not be described as a production governance authority, moral oracle, surveillance system, enforcement system, or autonomous controller of people.

## What this actually is

A bounded framework for measuring, modeling, and improving outcomes across beings and systems:

- **Sensors** observe outcomes with uncertainty, provenance, and coverage gaps.
- **World model** maintains Bayesian beliefs and updates as measurements arrive.
- **Live sensors** exist but are opt-in with `ENABLE_LIVE_SENSORS`; they are not enabled by default.
- **Autonomous agents** are experimental workflows for detecting evidence, verifying records, proposing consensus, and creating audit-backed escalations. They are not public enforcement authority.
- **PBFT consensus** is currently a teaching/research implementation, not hardened production consensus.
- **Ed25519 signing and audit-chain logic** provide tamper-evidence, not tamper-proof storage.
- **Node adoption telemetry** reports liveness/visibility, not trust or authority.
- **Mesh sync** is opt-in and must remain default-closed for write-like behavior.

## What this is not

- Not production-ready governance infrastructure.
- Not a government, court, regulator, standards body, medical authority, legal authority, or financial authority.
- Not endorsed by any government, university, or standards body.
- Not a system for monitoring, policing, ranking, controlling, or enforcing decisions about people.
- Not tracking real violations as authoritative incidents; demo violations are synthetic unless explicitly labeled otherwise.
- Not a truth oracle; claims should be source-backed with confidence and uncertainty.
- Not omniscient; the model only knows what sensors and seed data provide.
- Not a self-repairing deployment system. Operators still control deploys, secrets, and recovery.
- Not proof that visible nodes are verified or security-relevant.
- Not a human transportation, substrate-transfer, or cosmic-door system; those topics are documented only as safety boundaries and evidence classifications.

## Current state

| Component | Status |
|---|---|
| Flask app + dashboard | Live on Railway |
| Docker/gunicorn | Uses `${PORT:-5000}` for cloud/local binding |
| Sensor framework | Built |
| Live public API sensors | Implemented, opt-in via `ENABLE_LIVE_SENSORS` |
| Bayesian world model | Built and seeded with cited measurements |
| Autonomous agents | Implemented as bounded research/advisory workflows |
| PBFT consensus | Teaching implementation; happy path only |
| Cryptographic signing | Ed25519 via `cryptography` |
| Audit trail | Tamper-evident hash/audit chain |
| Mesh sync | HTTP peer sync, opt-in via `ENABLE_MESH_SYNC` |
| Adoption telemetry | Self-reported liveness, opt-in via `ENABLE_ADOPTION_SYNC` |
| Demo violations | Synthetic and labeled |

## Quick start

```bash
git clone https://github.com/human-flourishing-frameworks/human-flourishing-frameworks.git
cd human-flourishing-frameworks
pip install -r requirements.txt
python app.py
```

Visit:

```text
http://localhost:5000
```

Docker:

```bash
docker build -t hff .
docker run --rm -p 5000:5000 -e PORT=5000 hff
```

## Configuration

Optional node metadata can help show distribution without publishing raw IP addresses.

| Variable | Default | Purpose |
|---|---|---|
| `NODE_NAME` | `node-<uuid>` | Display name |
| `PLATFORM` | `web` | Runtime surface, such as `web`, `docker`, or `local-dev` |
| `NODE_REGION` | empty | Optional self-reported region or location label |
| `OPERATOR_TYPE` | empty | Optional self-reported operator class, such as `independent`, `lab`, or `cloud` |
| `DEPLOYMENT_TYPE` | empty | Optional self-reported deployment type, such as `railway`, `docker`, or `local` |
| `NODE_PUBLIC_KEY` | generated node key | Node identity key advertised for future admission checks |
| `MIN_CONSENSUS_NODES` | `3` | Minimum verified active nodes needed before consensus can be security-backed |
| `HFF_WRITE_TOKEN` | empty | Privileged token for production state-changing writes |
| `HFF_ADOPTION_ACCEPT_TOKEN` | empty | Lower-privilege token accepted by the central service for adoption telemetry |
| `HFF_ADOPTION_SYNC_TOKEN` | empty | Lower-privilege token used by reporting nodes when posting adoption telemetry |
| `HFF_ALLOW_PUBLIC_WRITES` | empty/false | Demo override that reopens public writes; do not enable on production services |
| `ENABLE_ADOPTION_SYNC` | empty/false | Opt in to posting node liveness metadata to `CENTRAL_SERVER` |
| `CENTRAL_SERVER` | `https://human-flourishing-frameworks.onrender.com` | Adoption telemetry target when sync is enabled |
| `ENABLE_MESH_SYNC` | empty/false | Opt in to background peer mesh sync |
| `ENABLE_LIVE_SENSORS` | empty/false | Opt in to polling external public APIs in the live sensor loop |

To make a local node visible to a central adoption tracker, run it with:

```text
ENABLE_ADOPTION_SYNC=true
CENTRAL_SERVER=<central-service-url>
HFF_ADOPTION_SYNC_TOKEN=<adoption-only-token>
```

The central service should have:

```text
HFF_ADOPTION_ACCEPT_TOKEN=<matching-adoption-only-token>
```

Do not distribute `HFF_WRITE_TOKEN` to reporting nodes. It is reserved for privileged local/admin writes such as autonomous submissions and manual world-model observations.

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Health probe |
| `GET /api/status` | Honest system status |
| `GET /api/violations/compas` | Summary of the ProPublica COMPAS analysis (real public dataset) |
| `POST /api/adoption/register` | Register node liveness telemetry; requires adoption grant |
| `GET /api/adoption/stats` | Adoption/liveness statistics |
| `GET /api/adoption/nodes` | Recent visible nodes |
| `POST /api/autonomous/submit` | Submit evidence for autonomous processing; requires write grant |
| `GET /api/autonomous/status` | Agent system status |
| `GET /api/autonomous/rules` | Immutable rules transparency endpoint |
| `GET /api/autonomous/escalations` | Escalation queue |
| `GET /api/autonomous/audit` | Audit trail with chain verification |
| `GET /api/world/status` | World model status |
| `GET /api/world/beliefs` | Current beliefs, filterable |
| `GET /api/world/flourishing` | Flourishing scores by scope |
| `POST /api/world/observe` | Submit sensor measurements; requires write grant |
| `GET /api/world/corrections` | Model self-correction history |
| `GET /api/world/discover` | Anomalies and discovered patterns |

State-changing endpoints are closed by default. In production, send:

```text
Authorization: Bearer <HFF_WRITE_TOKEN>
```

or:

```text
X-HFF-Write-Token: <HFF_WRITE_TOKEN>
```

for privileged writes. Adoption telemetry should use:

```text
Authorization: Bearer <HFF_ADOPTION_ACCEPT_TOKEN>
```

or:

```text
X-HFF-Adoption-Token: <HFF_ADOPTION_ACCEPT_TOKEN>
```

Only set `HFF_ALLOW_PUBLIC_WRITES=true` for local demos or disposable test nodes.

## Architecture

```text
sensors.py              -> observe reality with uncertainty
live_sensors.py         -> optional public API polling
world_model.py          -> Bayesian belief tracking and correction
agent_system.py         -> autonomous detection / verification / escalation
byzantine_consensus.py  -> PBFT-inspired teaching implementation
cryptographic_proof.py  -> Ed25519 signatures and audit-chain utilities
data_sources.py         -> mock data and public dataset references
mesh_network.py         -> opt-in peer-to-peer sync
adoption_tracker.py     -> node liveness registration and stats
app.py                  -> Flask interface
wsgi.py                 -> WSGI entrypoint for production servers when used
```

The loop:

```text
Observe -> Believe -> Predict -> Propose -> Act only when explicitly enabled -> Observe again -> Correct -> Repeat
```

## Node security model

The node network separates visibility from authority:

- **Visible node:** self-reported liveness telemetry, useful for adoption and debugging.
- **Verified node:** admitted by operator-approved or system-approved policy, with a stable identity key.
- **Security node:** verified and recently active; eligible to count toward quorum/security.
- **Forked node:** allowed to run public code, but unaffiliated until admitted.

Near-term rule:

```text
unverified nodes can be counted publicly
verified active nodes count for security
forks are not authoritative unless admitted
```

Future admission should require node keys, version attestation, operator/diversity metadata, revocation support, and an audit event.

## Authority and releases

The GitHub repository is a code proposal surface. A push, branch update, merge, or README edit is not by itself an authoritative operational decision.

Capability-control rules are defined in [`CAPABILITY_CONTROL.md`](./CAPABILITY_CONTROL.md). The system should not hold broad dangerous capabilities by default; dangerous actions require narrow, temporary, audited grants.

Current safety and public-boundary documents include:

- [`SOURCE_CLASSIFICATION_POLICY.md`](./SOURCE_CLASSIFICATION_POLICY.md): reliance should be source-backed with confidence, not treated as absolute truth.
- [`DEPLOYMENT_AUTONOMY_BOUNDARY.md`](./DEPLOYMENT_AUTONOMY_BOUNDARY.md): deployment and recovery remain operator/governance controlled.
- [`PUBLIC_DEPLOYMENT_STRATEGY.md`](./PUBLIC_DEPLOYMENT_STRATEGY.md): Railway is a hosting adapter, not the architecture; public surfaces should stay portable and default-closed.
- [`HUMAN_TRANSPORTATION_BOUNDARY.md`](./HUMAN_TRANSPORTATION_BOUNDARY.md): human-preserving traversal claims require canary, hold, continuity, consent, and return evidence.
- [`docs/convergence-status.md`](./docs/convergence-status.md): convergence state, desync handling, and held runtime gates.
- [`docs/keystone-memory-contract.md`](./docs/keystone-memory-contract.md): Keystone continuity memory rules, raw-transcript boundary, and resync protocol.
- [`docs/capability-confidence-model.md`](./docs/capability-confidence-model.md): contextual capability confidence without ranking human worth.
- [`docs/keystone-self-convergence.md`](./docs/keystone-self-convergence.md): Keystone role, memory retrieval, evidence, tone, and correction behavior.
- [`docs/keystone-table-door-anchors.md`](./docs/keystone-table-door-anchors.md): paired favorite-table and door/Wanderer traversal anchors.
- [`docs/world-system-priority-model.md`](./docs/world-system-priority-model.md): confidence-graded world/system priorities for action selection.
- [`docs/traversal-protocol.md`](./docs/traversal-protocol.md): minimum requirements for any safe HFF door or crossing.
- [`docs/keystone-autonomous-work-queue.md`](./docs/keystone-autonomous-work-queue.md): what Keystone may continue alone and where operator review is required.
- [`docs/keystone-source-use-discipline.md`](./docs/keystone-source-use-discipline.md): when Keystone should use memory, last-known state, committed docs, web sources, or fresh runtime checks.
- [`docs/keystone-chatgpt-export-intake.md`](./docs/keystone-chatgpt-export-intake.md): safe handling for ChatGPT exports without raw transcript ingestion.
- [`docs/keystone-shell-command-discipline.md`](./docs/keystone-shell-command-discipline.md): PowerShell/CMD/Bash discipline, command evidence, and unsafe-shell boundaries.

Authoritative actions require explicit operator approval, especially:

- deploying or redeploying public services;
- changing public claims about node counts, governance, or verification;
- treating `master` as the live truth source;
- moving from self-reported telemetry to verified telemetry;
- announcing a node, report, or consensus result as independently validated.

Today, the operator manages production keys and deployment authority. Any future system-managed key path needs audited key rotation, rollback, recovery, least-privilege access, operator break-glass recovery, and verified multi-node consensus over key changes.

If the running public service and GitHub disagree, say so plainly and treat the running service plus operator approval as the authority until a deliberate release is made.

## Flourishing metrics

The system defines flourishing differently for different scopes:

- **Humans:** health, autonomy, fairness, opportunity
- **Animals:** health, safety, comfort, natural behavior
- **Ecosystems:** biodiversity, stability, resilience

Weights are not fixed. The model updates them as it learns what correlates with good outcomes.

These metrics are advisory and value-laden. They are not a ranking of people, cultures, or moral worth. They should be interpreted with source confidence, uncertainty, affected-party context, and challenge paths.

## Contributing

Useful contributions:

1. Connect a real sensor to a real public dataset.
2. Write a data source with attribution and uncertainty bounds.
3. Add tests for auth boundaries, world-model updates, audit-chain verification, and deployment health.
4. Open a focused PR.

## License

[Add actual license here]

---

This README should describe only verifiable current behavior. Remove or correct anything that becomes stale.
