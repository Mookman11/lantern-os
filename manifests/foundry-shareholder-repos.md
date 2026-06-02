# FOUNDRY Shareholder Repo Universe

Status: central consolidation map.

The FOUNDRY skill is the shareholder-facing consolidation layer for Lantern OS.
It treats these repositories as the current repo universe and keeps `lantern-os`
as the clean release/control plane.

## Canonical Remote

- `https://github.com/alex-place/lantern-os`

## Named Repositories

| Repo | Role | Promotion Policy |
|---|---|---|
| `https://github.com/alex-place/lantern-os` | clean v1.0.0 control plane | promote validated artifacts here |
| `https://github.com/alex-place/place_co` | web/company surface | source evidence; do not overwrite blindly |
| `https://github.com/alex-place/gm-agent-orchestrator` | agent/orchestrator source | source evidence; dirty state is high risk |
| `https://github.com/alex-place/lantern-symbolic-sandbox` | symbolic Lantern language sandbox | source evidence and quarantine rails |
| `https://github.com/alex-place/ChildOfLevistus` | GameMaker/game source | source evidence |
| `https://github.com/alex-place/gamemaker-room-editor` | GameMaker tooling | source evidence |
| `https://github.com/alex-place/moneybags` | Java/public money tooling | source evidence |
| `https://github.com/alex-place/SmartBid` | legacy Java bidding app | source evidence |
| `https://github.com/alex-place/smartmealplanning` | legacy Java meal planner | source evidence |

## Offline Token Rule

Offline-only/local/server-farm Foundry tokens are unmetered internal capacity.
They are not called "Lite", not rated per token, and not billed as cloud burn.
Capacity is bounded by owned hardware, queue time, thermals, power, storage,
network, maintenance, and operator policy.

Cloud/API escalation remains metered by actual provider pricing and must be
reported separately.

## Hardware Expansion Queue

| Node | Target | Status | Boundary |
|---|---|---|---|
| Primary Windows PC | Lantern surface + first dual-boot target | prep-ready, install-held | physical partition/install action required |
| Son's PC | second dual-boot target | candidate | needs read-only hardware/readiness check first |
| iPhone | Foundry edge node | candidate | use app/shortcut/SSH/web surface first; true dual boot held |
| Second phone | second phone edge node | candidate | identify device/OS before any boot claim |
| Server farm | Foundry local inference pool | candidate | inventory nodes, power, GPUs/NPUs, network, storage |

Matrix RAG architecture:
`manifests/FOUNDRY-MATRIX-RAG-DOLLHOUSE.md`

## iPhone Boundary

Apple documents an iPhone/iPad secure boot chain where startup components are
cryptographically signed and verified:
`https://support.apple.com/guide/security/boot-process-for-iphone-and-ipad-devices-secb3000f149/web`.
Therefore, iPhone is not treated as a normal PC-style dual-boot target. Use it
first as a secure Foundry edge node:

- mobile dashboard;
- local capture and review station;
- private relay into the server farm;
- shortcut-driven task intake;
- on-device model or app runtime where supported.

Any true phone dual boot remains held until the exact device model, backup,
boot path, legal/security risk, and rollback path are verified.

## Shareholder Rule

Shareholder-facing material must separate:

- verified local repo state;
- source-repo evidence;
- operator assertions;
- cloud metered costs;
- offline/local/server-farm unmetered capacity;
- speculative future revenue.
