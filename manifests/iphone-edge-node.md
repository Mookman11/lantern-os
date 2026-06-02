# iPhone Foundry Edge Node

Status: candidate.

The iPhone path is not a normal dual-boot path. It is a mobile command/capture
surface for the local Matrix RAG dollhouse.

## First Interface

Use one or more:

- Apple Shortcuts action that sends text/audio/photo capture to a local Foundry
  endpoint;
- mobile web dashboard on the LAN;
- SSH client app for operator-only terminal access;
- secure file drop into an ingest folder;
- Apple Intelligence Shortcuts action when available on the device.

## Data Lanes

| Lane | Input | Destination | Output |
|---|---|---|---|
| Capture | typed note, voice transcript, photo, URL | ingest worker | queued artifact |
| Approve | task decision | orchestrator/dashboard | allowed action |
| Query | question | local RAG endpoint | evidence pack |
| Review | shareholder packet | phone browser/PDF viewer | approval or edits |

## Local Endpoint Shape

```text
POST /foundry/capture
POST /foundry/query
POST /foundry/approve
GET  /foundry/status
```

## Safety Boundary

- Keep the phone as an edge node first.
- Do not claim true phone dual boot without exact model, backup, boot path,
  risk, and rollback evidence.
- Prefer LAN/VPN/local relay over public tunnels.
- Verify tunnels before trusting remote endpoints.

## Operator Questions To Fill

| Field | Value |
|---|---|
| iPhone model | TBD |
| iOS version | TBD |
| Apple Intelligence available? | TBD |
| Shortcuts allowed? | TBD |
| LAN/VPN path | TBD |
| Backup current? | TBD |
