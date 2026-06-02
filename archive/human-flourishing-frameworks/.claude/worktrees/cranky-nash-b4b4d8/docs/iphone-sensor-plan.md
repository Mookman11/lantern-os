# iPhone Sensor Plan

Status: docs-only implementation plan.

Last reviewed: 2026-05-09.

## Purpose

Make Alex's iPhone usable as a low-friction HFF/Keystone sensor without turning it into a surveillance device.

The first version should be a **phone heartbeat / operator presence sensor**, not a full personal-data collector.

## Why this is useful

The current operator workflow already needs an easy iPhone path:

```text
Alex can send short commands from iPhone.
Keystone can check a GitHub issue inbox on demand.
The phone can also report a minimal heartbeat so HFF can distinguish no visible nodes from at least one opted-in operator device.
```

This helps with convergence because the public adoption endpoints have repeatedly shown no visible polling nodes. A phone heartbeat can prove one intentionally opted-in personal node exists without needing a laptop, shell session, or long LLM handoff.

## Existing compatible surface

HFF already has a gated adoption telemetry surface:

```text
POST /api/adoption/register
GET /api/adoption/stats
GET /api/adoption/nodes
```

The adoption register path records node liveness metadata such as:

```text
node_id
node_name
platform
version
region
operator_type
deployment_type
node_public_key
```

Production adoption writes require an explicit grant token or demo override. The iPhone path should use that existing gate first rather than adding a new unauthenticated write surface.

## Version 0: iPhone as adoption heartbeat

Use iOS Shortcuts, or any phone automation client, to send a small authenticated JSON POST to the Render public surface:

```text
https://human-flourishing-frameworks.onrender.com/api/adoption/register
```

Suggested payload:

```json
{
  "node_id": "alex-iphone-001",
  "node_name": "Alex iPhone",
  "platform": "iphone_shortcuts",
  "version": "phone-heartbeat-v0",
  "region": "",
  "operator_type": "owner_operator",
  "deployment_type": "personal_phone_sensor",
  "node_public_key": ""
}
```

Suggested headers:

```text
Content-Type: application/json
Authorization: Bearer <HFF_ADOPTION_ACCEPT_TOKEN>
```

or:

```text
X-HFF-Adoption-Token: <HFF_ADOPTION_ACCEPT_TOKEN>
```

Keep the token in the iPhone automation tool only if Alex accepts the risk that the phone can submit adoption heartbeat writes. Do not store the token in the repo.

## What Version 0 must not collect

Do not collect by default:

```text
precise GPS location
contacts
messages
call logs
photos
microphone/audio
camera/video
health data
biometrics
sleep data
calendar contents
browser history
raw notification content
```

Do not infer private state from the phone heartbeat beyond:

```text
this opted-in phone sent a heartbeat at this time
```

## Optional manual fields

If Alex wants richer but still low-risk context, add it manually in the command inbox rather than automatic phone scraping:

```text
K SENSOR: awake=true energy=low location=home-ish work_mode=HFF
K SENSOR: going_to_sleep=true confidence=0.7
K SENSOR: dream_note="repo maze with GitHub issues"
```

These should remain operator-provided notes, not hidden background collection.

## Version 1: dedicated phone heartbeat endpoint

Only after Version 0 works, consider adding a small dedicated endpoint:

```text
POST /api/operator/phone/heartbeat
```

Minimum accepted fields:

```json
{
  "device_id": "alex-iphone-001",
  "signal_type": "heartbeat",
  "timestamp": "client optional; server timestamp wins",
  "battery_state": "optional coarse charging/discharging/full/unknown",
  "focus_mode": "optional coarse if manually allowed",
  "operator_note": "optional short text"
}
```

Rules:

```text
server timestamp is authoritative
unknown fields are rejected or ignored
precise location is rejected by default
free text is bounded and redacted if later exposed publicly
endpoint is default-closed unless explicitly enabled
writes require a phone-specific token separate from HFF_WRITE_TOKEN
```

## Version 2: phone as local sensor bridge

Only after a privacy review, the phone could become a local-first bridge for explicitly approved signals:

```text
manual check-in
charging state
coarse focus/work mode
coarse motion state such as stationary/walking/driving if explicitly approved
coarse sleep intent such as "going to sleep" if explicitly approved
```

This should remain opt-in and revocable.

## Suggested iPhone Shortcut shape

A simple shortcut can do:

```text
1. Text: JSON payload.
2. Get Contents of URL.
3. Method: POST.
4. Headers: Content-Type and adoption token.
5. Body: JSON.
6. Optional: show result.
```

Useful triggers:

```text
manual Home Screen button
when charger connects
when Focus mode changes, if Alex explicitly enables it
before sleep, if Alex manually runs it
```

Do not enable location, microphone, health, contacts, or message access for this shortcut.

## Validation

After a heartbeat POST, check:

```text
GET /api/adoption/stats
GET /api/adoption/nodes
```

Expected result:

```text
total_nodes increases or remains stable with last_seen updated
by_platform includes iphone_shortcuts
/api/adoption/nodes includes Alex iPhone with platform iphone_shortcuts
```

## Safety boundary

This plan does not authorize:

```text
secret commits
raw phone data storage
hidden tracking
precise location collection
health-data ingestion
audio/video capture
background surveillance
runtime endpoint changes without tests
public claims that phone telemetry proves Alex's state
```

## Recommended next action

Use Version 0 first:

```text
Create an iPhone Shortcut that sends an authenticated adoption heartbeat.
Then run the public adoption checks and record whether the phone appears as a visible node.
```

Only if Version 0 is too clunky should HFF add a dedicated phone endpoint.
