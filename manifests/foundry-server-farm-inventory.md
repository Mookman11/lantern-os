# FOUNDRY Server Farm Inventory

Status: empty schema, ready for operator fill-in.

Use this to convert "server farm" into measurable local capacity. Offline
Foundry tokens stay unmetered by vendor pricing, but capacity must be planned
against hardware, power, storage, network, thermals, and maintenance.

## Node Table

| Node ID | Hostname/IP | OS | CPU | RAM | GPU/NPU | VRAM | Storage Free | Network | Role | Status |
|---|---|---|---|---:|---|---:|---:|---|---|---|
| `foundry-01` | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | model server | candidate |
| `foundry-vector-01` | TBD | TBD | TBD | TBD | optional | TBD | TBD | TBD | Qdrant/vector | candidate |
| `foundry-ingest-01` | TBD | TBD | TBD | TBD | optional | TBD | TBD | TBD | document ingest | candidate |

## Services

| Service | Preferred Port | Node | Purpose | Validation |
|---|---:|---|---|---|
| Ollama API | `11434` | TBD | local model serving | `GET /` returns running |
| Qdrant API | `6333` | TBD | vector/hybrid retrieval | collections list reachable |
| Foundry dashboard | TBD | TBD | operator/iPhone control | login + local network only |
| Ingest worker | TBD | TBD | repo/PDF ingestion | dry-run index summary |

## Capacity Fields

Record these before claiming scale:

- owned vs rented hardware;
- average idle/load power;
- cooling constraints;
- local network bandwidth;
- storage endurance and backup;
- model sizes that fit in VRAM/RAM;
- embedding throughput;
- retrieval latency;
- maintenance owner;
- allowed remote access path.

## First Validation

```powershell
hostname
Get-ComputerInfo | Select-Object CsName, OsName, CsProcessors, CsTotalPhysicalMemory
Get-Volume
Get-NetIPAddress
```

Do not run destructive maintenance, driver changes, firmware updates, or remote
access changes during inventory.
